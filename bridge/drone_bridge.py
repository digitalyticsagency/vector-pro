#!/usr/bin/env python3
"""
VECTOR PRO — Drone Bridge
Consumes the WebSocket telemetry stream from the browser app and emits
MAVLink commands to a flight controller or SITL simulator.

Usage:
  python3 drone_bridge.py                         # dry-run, print commands only
  python3 drone_bridge.py --mavlink udp:127.0.0.1:14550   # ArduPilot SITL
  python3 drone_bridge.py --mavlink /dev/ttyUSB0  # real FC

Dependencies:
  pip install websockets pymavlink
"""
import asyncio
import json
import argparse
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [BRIDGE] %(message)s")
log = logging.getLogger(__name__)

FAILSAFE_TIMEOUT = 0.8   # seconds of silence before zeroing commands

try:
    import websockets
except ImportError:
    raise SystemExit("pip install websockets")

mav = None

def init_mavlink(conn_str):
    global mav
    try:
        from pymavlink import mavutil
        mav = mavutil.mavlink_connection(conn_str)
        mav.wait_heartbeat(timeout=5)
        log.info(f"MAVLink heartbeat on {conn_str}")
    except Exception as e:
        log.error(f"MAVLink init failed: {e}")
        mav = None

def send_command(yaw_rate, pitch_rate, fwd_vel):
    """Send SET_ATTITUDE_TARGET or body-rate command to the FC."""
    if mav is None:
        # dry-run
        log.info(f"CMD  yaw={yaw_rate:+.3f}  pitch={pitch_rate:+.3f}  fwd={fwd_vel:+.3f}")
        return
    # Use SET_POSITION_TARGET_LOCAL_NED body-frame velocity
    try:
        from pymavlink.dialects.v20 import ardupilotmega as mavlink2
        mav.mav.set_position_target_body_ned_send(
            int(time.time() * 1000) & 0xFFFFFFFF,  # timestamp ms
            mav.target_system, mav.target_component,
            mavlink2.MAV_FRAME_BODY_NED,
            0b0000111111000111,  # ignore pos, use vx vy vz yaw_rate
            0, 0, 0,            # x y z position (ignored)
            fwd_vel, 0, -pitch_rate,   # vx vy vz
            0, 0, 0,            # afx afy afz
            0, yaw_rate,        # yaw, yaw_rate
        )
    except Exception as e:
        log.error(f"MAVLink send error: {e}")

async def serve(ws, mavlink_conn=None):
    log.info(f"Browser connected: {ws.remote_address}")
    last_cmd_t = time.monotonic()

    async def failsafe_loop():
        nonlocal last_cmd_t
        while True:
            await asyncio.sleep(0.1)
            if time.monotonic() - last_cmd_t > FAILSAFE_TIMEOUT:
                send_command(0, 0, 0)   # decay to neutral

    task = asyncio.create_task(failsafe_loop())
    try:
        async for msg in ws:
            data = json.loads(msg)
            if data.get("type") == "track":
                cmd = data.get("cmd", {})
                send_command(
                    cmd.get("yaw_rate", 0),
                    cmd.get("pitch_rate", 0),
                    cmd.get("fwd_vel", 0),
                )
                last_cmd_t = time.monotonic()
    except Exception as e:
        log.warning(f"Connection closed: {e}")
    finally:
        task.cancel()
        send_command(0, 0, 0)
        log.info("Browser disconnected — all commands zeroed")

async def main(host, port, mavlink_conn):
    if mavlink_conn:
        init_mavlink(mavlink_conn)

    log.info(f"VECTOR PRO bridge listening on ws://{host}:{port}")
    async with websockets.serve(lambda ws: serve(ws, mavlink_conn), host, port):
        await asyncio.Future()   # run forever

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--mavlink", default=None, help="MAVLink connection string")
    args = ap.parse_args()
    asyncio.run(main(args.host, args.port, args.mavlink))

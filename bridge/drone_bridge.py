#!/usr/bin/env python3
"""VECTOR PRO Drone Bridge — full version in bridge/drone_bridge.py"""
import asyncio,json,logging
logging.basicConfig(level=logging.INFO)
try:
    import websockets
except ImportError:
    raise SystemExit('pip install websockets')
async def serve(ws):
    async for msg in ws:
        d=json.loads(msg)
        if d.get('type')=='track':
            c=d.get('cmd',{})
            print(f"YAW={c.get('yaw_rate',0):+.3f} PITCH={c.get('pitch_rate',0):+.3f} FWD={c.get('fwd_vel',0):+.3f} SPEED={d.get('speed_kmh',0):.1f}km/h")
async def main():
    async with websockets.serve(serve,'0.0.0.0',8765):
        print('Bridge on ws://0.0.0.0:8765'); await asyncio.Future()
asyncio.run(main())

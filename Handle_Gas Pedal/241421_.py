from dynamixel_sdk import *

port = PortHandler('/dev/ttyACM0')
pack = PacketHandler(2.0)


if not port.openPort():
    print("포트를 열 수 없습니다.")
    exit(1)

if not port.setBaudRate(1000000):
    print("보드레이트 설정 실패")
    exit(1)

IDS = [5, 6]

for i in IDS:
    pack.write1ByteTxRx(port, i, 64, 0)
    pack.write1ByteTxRx(port, i, 11, 3)
    pack.write1ByteTxRx(port, i, 64, 1)
    pack.write4ByteTxRx(port, i, 116,0)

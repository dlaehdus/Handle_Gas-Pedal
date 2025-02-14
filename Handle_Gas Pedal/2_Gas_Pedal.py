from dynamixel_sdk import *


port = PortHandler('/dev/ttyACM0')
pack = PacketHandler(2.0)

if not port.openPort():
    print("포트를 열 수 없습니다.")
    exit(1)

if not port.setBaudRate(1000000):
    print("보드레이트 설정 실패")
    exit(1)

IDS = [1,2]

for dxl_id in IDS:
    pack.write1ByteTxRx(port, dxl_id, 64, 0)
    pack.write1ByteTxRx(port, 1, 11, 1)
    pack.write1ByteTxRx(port, 2, 11, 5)
    pack.write2ByteTxRx(port, 2, 102, 50) # 전류를 설정할때는 2바이트
    pack.write1ByteTxRx(port, dxl_id, 64, 1)

pack.write4ByteTxRx(port, 2, 116, -400)

def read_position():
    position, _, _ = pack.read4ByteTxRx(port, 2, 132)
    position = position if position < (1 << 31) else position - (1 << 32)
    if position <= -800 or position >= 0:
        pack.write2ByteTxRx(port, 2, 102, 1000)  # 전류 증가
    else:
        pack.write2ByteTxRx(port, 2, 102, 50)    # 기본 전류 유지
    return position

def write_velocity(position):
    velocity = position+400
    pack.write4ByteTxRx(port, 1, 104, velocity)

try:
    while True:
        pos = read_position()
        write_velocity(pos)
        print(pack.read4ByteTxRx(port, 1, 128))
except KeyboardInterrupt:
    print("프로그램 종료")
    
finally:
    pack.write1ByteTxRx(port, 1, 64, 0)
    pack.write1ByteTxRx(port, 2, 64, 0)
    port.closePort()

#속도계를 제대로 나타내야함, 프로그램 종료시 토크를 제거해야함
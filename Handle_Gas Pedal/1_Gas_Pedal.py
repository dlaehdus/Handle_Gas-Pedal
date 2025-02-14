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
    pack.write2ByteTxRx(port, 2, 38, 50) # 전류를 설정할때는 2바이트
    pack.write1ByteTxRx(port, dxl_id, 64, 1)

def read_position():
    position, _, _ = pack.read4ByteTxRx(port, 2, 132)
    return position

def write_velocity(position):
    velocity = abs(position) + 400
    pack.write4ByteTxRx(port, 1, 104, velocity)

try:
    while True:
        pos = read_position()
        write_velocity(pos)
        print(pack.read4ByteTxRx(port, 1, 128))
except KeyboardInterrupt:
    print("프로그램 종료")
    pack.write4ByteTxRx(port, IDS, 64, 0)  # 1번 모터 속도 0으로 정지
    port.closePort()

#컨트롤러의 제한 범위 설정이 필요함
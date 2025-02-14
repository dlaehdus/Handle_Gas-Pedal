from dynamixel_sdk import *
import sys, termios, tty, select, time

# 비차단 키 입력을 위한 함수
def get_key(timeout=0.1):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([fd], [], [], timeout)
        if rlist:
            return sys.stdin.read(1)
        else:
            return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# 포트 및 패킷 핸들러 초기화
port = PortHandler('/dev/ttyACM0')
pack = PacketHandler(2.0)

if not port.openPort():
    print("포트를 열 수 없습니다.")
    exit(1)

if not port.setBaudRate(1000000):
    print("보드레이트 설정 실패")
    exit(1)

IDS = [1, 2]

# 초기 설정: 우선 토크 비활성화 후 설정값 적용
for dxl_id in IDS:
    pack.write1ByteTxRx(port, dxl_id, 64, 0)
pack.write1ByteTxRx(port, 1, 11, 1)
pack.write1ByteTxRx(port, 2, 11, 5)
pack.write2ByteTxRx(port, 2, 102, 50)  # 전류 설정 (2바이트)
for dxl_id in IDS:
    pack.write1ByteTxRx(port, dxl_id, 64, 1)

pack.write4ByteTxRx(port, 2, 116, -400)

def read_position():
    position, _, _ = pack.read4ByteTxRx(port, 2, 132)
    position = position if position < (1 << 31) else position - (1 << 32)
    if position <= -1100 or position >= 200:
        pack.write2ByteTxRx(port, 2, 102, 1000)  # 전류 증가
    else:
        pack.write2ByteTxRx(port, 2, 102, 50)    # 기본 전류 유지
    return position

def write_velocity(position):
    velocity = int((position + 400) / 2)
    pack.write4ByteTxRx(port, 1, 104, velocity)

print("백스페이스 키(DEL 또는 백스페이스)를 누르면 종료됩니다.")
try:
    while True:
        pos = read_position()
        write_velocity(pos)
        vel, _, _ = pack.read4ByteTxRx(port, 1, 128)
        if vel >= (1 << 31):
            vel -= (1 << 32)  # 음수 처리
        print('현재속도:', -vel)
        # 키 입력 확인 (백스페이스: ASCII 127 혹은 '\b')
        key = get_key()
        if key in ['\x7f', '\b']:
            print("백스페이스 키가 감지되어 종료합니다.")
            break
except KeyboardInterrupt:
    print("KeyboardInterrupt 발생. 프로그램 종료")
finally:
    # 종료 전 토크 비활성화 명령 후 약간의 딜레이를 추가
    pack.write4ByteTxRx(port, 1, 104, 0)
    pack.write4ByteTxRx(port, 2, 116, -400)
    for dyna in IDS:
        pack.write1ByteTxRx(port, dyna, 64, 0)
    time.sleep(0.1)
    port.closePort()

    #해결완료
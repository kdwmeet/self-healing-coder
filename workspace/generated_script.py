# 첫 번째 시도: 일부러 print를 잘못 적어 NameError를 발생시키기
try:
    # 20개의 피보나치 수열을 생성 (1, 1, 2, 3, ...)
    fibs = []
    a, b = 1, 1
    for _ in range(20):
        fibs.append(a)
        a, b = b, a + b

    # 의도적으로 함수 이름을 잘못 써서 NameError 발생시키기
    prnt("첫 번째 시도(의도적 오류) - 이 줄에서 NameError가 발생해야 합니다.")
    prnt(f"생성된 피보나치(첫 20개): {fibs}")
except NameError as e:
    # 발생한 NameError를 잡아 출력
    print("첫 번째 시도에서 발생한 에러를 포착했습니다:", e)

# 두 번째 시도: 오류를 수정해서 정상 출력
# 정상적으로 print를 사용하여 결과를 출력
print("\n두 번째 시도(수정됨) - 정상 실행 결과:")
for idx, val in enumerate(fibs, start=1):
    print(f"{idx}: {val}")
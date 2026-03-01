import anyio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Path, Query, Body, status, HTTPException, Depends, BackgroundTasks
from sqlalchemy import select
from db_connection import SessionFactory, get_session
from models import User
from schema import UserSignUpRequest, UserResponse, UserUpdateRequest

def send_email(name: str):
    import time
    time.sleep(5)  # 5초 대기
    print(f"{name}님에게 이메일을 보냈습니다.")

@asynccontextmanager
async def lifespan(_):
    # 서버 실행될 때, 실행되는 부분
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 200 # 스레드 풀 개수를 200개로 증량
    yield
    # 서버 종료될 때, 실행되는 부분

# lifespan -> FastAPI 서버가 실행되고 종료될 때, 특정 리소스를 생성하고 정리하는 기능
app = FastAPI(lifespan=lifespan)

# 1. 데이터를 밖으로 빼서 어디서든 접근 가능하게 합니다.
# users = [
#     {"id": 1, "name": "alex", "age": 20},
#     {"id": 2, "name": "tom", "age": 30},
#     {"id": 3, "name": "hank", "age": 40},
#     {"id": 4, "name": "jane", "age": 50},
#     {"id": 5, "name": "mike", "age": 60},
# ]

# 전체 사용자 조회 API
@app.get("/users",
        response_model=list[UserResponse], # 응답은 UserResponse 형태의 리스트로 반환하겠다.
        status_code=status.HTTP_200_OK
        )
def get_users_handlers(
    session = Depends(get_session) # get_session 함수의 반환값을 session 매개변수로 전달
):

    #statement: 구문 -> SELECT * FROM user
    stmt = select(User)
    result = session.execute(stmt)
    users = result.scalars().all() # scalars() -> User 객체만 뽑아서 반환, all() -> 전체 결과를 리스트로 반환
    return users

# 회원 검색 API
# @app.get("/users/search")
# def search_user_handler():
#     return {"msg": "Welcome"}

# {user_id}번 사용자 조회 API -> 단일
# Path(경로) + Parameter(매개변수) -> 동적으로 바뀌는 값을 한 번에 처리
# Path Parameter에 type hint 추가하면 -> 명시한 타입에 맞는지 검사 & 보장

# @app.get("/users/{user_id}")
# def get_user_handler(user_id: int):
#     # 1, 2, 3, 4
#     # 0, -1, -2, ...
#     if user_id < 1:
#         return {"msg": "잘못된 user_id 값입니다."}
#     return users[user_id - 1]

# @app.get("/users/{user_id}")
# def get_user_handler(
#     user_id: int = Path(..., ge=1, description="user_id는 1이상")
# ):
    # gt : 초과
    # ge : 이상
    # lt : 미만
    # le : 이하
    # max_digits: 최대 자리수 000000
    # return users[user_id - 1]

# GET /items/{item_name}
# item_name: str & 최대 글자수(max_length = 6)
# 응답 형식: {"item_name": ...}
items = [
    {"id": 1, "name": "apple"},
    {"id": 2, "name": "banana"},
    {"id": 3, "name": "cherry"},
]

@app.get("/items")
def get_item_handlers():
    return items

@app.get("/items/{item_name}")
def get_item_handler(
    item_name: str = Path(..., max_length=6, description="item_name는 문자형식이고 최대6자까지 가능")
):
    return {"item_name": item_name}


# Query Parameter
# google.com/search?q=...
# Path 뒤에 붙어서 key = value 형태로 오는 값
# 필터링, 정렬, 검색, 페이지네이션 등 데이터를 조회시 부가조건을 명시

@app.get("/users/search",
        response_model=list[UserResponse],
        status_code=status.HTTP_200_OK
        )
def search_user_handler(
    name: str = Query(..., min_length=2), # default=... 이랑 같은 의미
    age: int = Query(None, ge=1) # 선택적(optional)
):
    #name이라는 key로 넘어오는 Query Parameter 값을 사용하겠다.
    return {"id": 0, "name": name, "age": age}

# ?field=id => id값만 반환
# ?field=name => name 값만 반환
@app.get("/users/{user_id}",
        response_model=UserResponse,
        status_code=status.HTTP_200_OK
        )
def get_user_handler(
    user_id: int = Path(..., ge=1, description="user_id는 1이상"),
    session = Depends(get_session)
):
    stmt = select(User).where(User.id == user_id)
    result = session.execute(stmt)
    user = result.scalar_one_or_none() # scalar_one_or_none() -> 결과가 하나면 User 객체 반환, 결과가 없으면 None 반환, 결과가 여러 개면 에러 발생
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 사용자의 ID입니다.")
    
    return user


##################################################################################

#FastAPI의 핵심 동작이 Type Hints 위에 설계되어 있음

# 회원가입 API
# 회원가입에 필요한 데이터
# 휴대폰 번호 -> 토스
# 소셜 로그인 ->
# 하나의 계정 -> 두 가지 인증 (비밀번호 기반 / 간편 로그인)
@app.post(
        "/users/sign-up", 
        status_code=status.HTTP_201_CREATED,
        response_model=UserResponse # 응답은 UserResponse 형태로 반환하겠다.
        
        )
@app.post(
    "/users/sign-up", 
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
def sign_up_handler(
    body: UserSignUpRequest,
    background_tasks: BackgroundTasks,  # BackgroundTasks 객체를 주입
    session = Depends(get_session)  # <-- 의존성 주입 추가!
):
    # 1. 입력 데이터를 바탕으로 새로운 User 객체 생성
    new_user = User(name=body.name, age=body.age)

    # 2. DB 작업 (FastAPI가 주입해준 session 사용)
    session.add(new_user)
    session.commit()

    background_tasks.add_task(send_email, body.name)  # 회원가입이 완료된 후에 이메일 보내는 작업을 백그라운드로 등록
    return new_user
    
    
    # new_user = {
    #     "id": len(users) + 1,
    #     "name": body.name,
    #     "age": body.age
    # }
    # users.append(new_user)
    # # name, age만 응답 -> response_model이랑 안 맞음 -> FastAPI ResponseValidationError 발생

    # return {"name": body.name, "age": body.age}

################################################################################################

# 코딩할 때 Tips
'''
1. 입력(ex 데이터 전처리)
2. 연산
3. 출력
'''

# 사용자 정보 수정 API
# PUT -> {name, age} 한 번에 교체
# PATCH -> {name} 또는 {age} 일부분만 교체
@app.patch(
        "/users/{user_id}",
        status_code=status.HTTP_200_OK,
        response_model=UserResponse
        )
def update_user_handler(
    user_id: int = Path(..., ge=1),
    body: UserUpdateRequest = Body(...),
    session = Depends(get_session)
    
):
    if body.name is None and body.age is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name과 age 중 하나는 필수로 입력해야 합니다.")

    
    stmt = select(User).where(User.id == user_id)
    result = session.execute(stmt)
    user = result.scalar_one_or_none()
        
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 사용자의 ID입니다.")
        
    if body.name is not None:
        user.name = body.name
    if body.age is not None:
        user.age = body.age
        
    session.commit()

    return user

######################################################################

# 회원 탈퇴 API
@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_handler(
    user_id: int = Path(..., ge=1),
    session = Depends(get_session)
):
    stmt = select(User).where(User.id == user_id)
    result = session.execute(stmt)
    user = result.scalar_one_or_none()
        
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 사용자의 ID입니다.")
        
    session.delete(user)
    session.commit()
    
    return {"message": f"사용자 ID {user_id}가 성공적으로 삭제되었습니다."}
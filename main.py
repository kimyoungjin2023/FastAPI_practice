from fastapi import FastAPI

app = FastAPI()

users = [
    {"id": 1, "name" : "alex"},
    {"id": 2, "name" : "bob"},
    {"id": 3, "name" : "chris"},
]

def hello_world():
    return {"msg": "hello_world"}

# HTTP 요청 -> 게시물을 생성하고 싶다.
# HTTP Method: 행위
# URL: 대상

# Get /users
# DELETE /comments/1

# @: 데코레이터 문법
# 섭에 GET /hello 요청이 들어오면, root_handler를 실행한다.
@app.get("/hello")
def hello_handler():
    # AI 추론
    return {"ping":"pong!!!!"}
    # return hello_world()


# 전체 사용자 조회 API
@app.get("/users") # 복수형
def get_user_handlers():
    return users


# 단일(1번) 사용자 조회 API
# GET /users/1
@app.get("/users/1")
def get_first_handler():
    return users[0]


# {user_id}번 사용자 조희 API
# Path(경로) + Parameter(매게변수) -> 동적으로 바뀌는 값을 한 번에 처리
@app.get("/users/{user_id}")
def get_user_handler(user_id: int):
    return users[user_id -1]
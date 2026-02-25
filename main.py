from fastapi import FastAPI, Path, Query

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


# # 전체 사용자 조회 API
# @app.get("/users") # 복수형
# def get_user_handlers():
#     return users


# # 단일(1번) 사용자 조회 API
# # GET /users/1
# @app.get("/users/1")
# def get_first_handler():
#     return users[0]


# Query Parameter
# google.com/search?q=python
# -> ?key=value 형태로 Path뒤에 붙는값
# 데이터 조회시 부가 조건을 명시(필터팅, 정렬, 검색, 페이지네이션 등)
@app.get("/users/search")
def search_user_handler(
    # name이라는 key로 넘어오는 Query Parameter 값을 사용하겠다.
    name: str = Query(..., min_length=2),# ... -> 필수값(required)
    age: int = Query(None, ge=1),# default값 지정 -> 선택적(optional)
):
    #name이라는 key로 넘어오는 Query Parameter 값을 사용하겠다.
    # GET 127.0.0.1:8000/users/search?name=alex
    return {"name": name,"age": age}



# {user_id}번 사용자 조희 API
# Path(경로) + Parameter(매게변수) -> 동적으로 바뀌는 값을 한 번에 처리
# Path Parameter에 type hint 추가하면 -> 명시한 타비에 맞는지 검사 & 보장

# ?field=id -> id값만 반환
# ?field=name -> name값만 반환
# 없으면 -> id,name 반환

# GET /users/1?field=id -> id 반환
# GET /users/1?field=name -> name 반환
# GET /users/1 -> id, name 반환
@app.get("/users/{user_id}")
def get_user_handler(
    user_id: int = Path(...,ge=1, description="사용자의 ID"),
    field:str = Query(None, description="출력할 필드 선택(id 또는 name)"),               
                     
):
    user = users [user_id -1]

    if field in ("id","name"):
        return {field:user[field]}
    return user
    # if field == "id":
    #     return user["id"]
    # if field == "name":
    #     return user["name"]
    # else:
    #     return user
    # gt :초과
    # ge: 이상
    # lt: 미만
    # le: 이하
    # max_digits: 최대 자리수 000000
    # min도 있음
    # return users[user_id -1]    


# 회원가입 API
# HTTP Method: GET, POST, PUT, PATCH, DELETE
# @app.post("/users/sign-up")
# def signup_user_handler():
#     return {"msg":"hello"}
#snake case

# 회원조회 API
# @app.get("/users/search")
# def search_user_handler():
#     return {"msg":"hello"}


# 주문 취소 : oders/1/cancel

# 1번 댓글(comment) 조회
# GET /comments

# 10번 댓글 삭제
# DELETE /comments/10

# 새로운 댓글 생성
# POST /comments

# comments 집단에 POST


# 요청 = HTTP Method(동작, verb) + URL(대상, object)


################실습################
# GET /items/{item_name}
# item_name: str & 최대 글자수(max_length) 6
# 응답: {"item_name":...}
item = [
    {"id":1, "name":"apple"},
    {"id":2, "name":"banana"},
    {"id":3, "name":"cherry"},
]

@app.get("/items/{item_name}")
def get_item_handler(item_name : str = Path(...,max_length = 6)):
    return {"item_name": item_name}



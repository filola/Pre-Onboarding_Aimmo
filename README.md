# Pre-Onboarding_Aimmo
# Aimmo 개발 과제 - 게시판 Restful API

#### - 게시물 카테고리 및 필터 적용
#### - 게시글 검색 기능 추가
#### - 댓글 및 대댓글 기능 추가
#### - 게시물 조회수 구현

---

## 구현한 방법과 이유에 대한 간략한 내용

### 사용자

- 유효성, 중복, 암호화를 고려한 회원가입 (보안강화)
- JWT 토큰을 사용하여 사용자의 인증과 인가 기능 구현 (게시판 수정 및 삭제 권한)

### 게시판

- 게시글을 읽기 위한 별도의 자격은 없음 (비회원 게시글 확인 가능)
- 게시글을 작서하기 위하여 사용자 로그인 필요
- 게시글을 작성한 사용자는 자신이 로그인 시 발급되는 JWT 토큰을 활용하여 확인하였고, 각 사용자는 본인의 게시물만 수정 및 삭제 가능 (타 유저 게시글 수정 및 삭제 불가)
- 게시글에 카테고리를 적용하여 필터를 통해 원하는 카테고리의 게시물만 접근 가능
- 게시글 검색 기능을 추가하여 검색어를 통해 원하는 게시물 검색 가능
- 댓글과 그 댓글의 댓글을 구현하고 pagination을 통해 한번의 모든 댓글들이 아닌 정해진 수량만큼 볼 수 있다.
- 조회수를 통해 어떠한 글이 많은 사용자가 접근했는지 알 수 있고 쿠키를 통한 조회수 구현을 통해 한 사용자가 조회수를 중복으로 증가시킬 수 없게 구현
---

## 자세한 실행 방법(endpoint 호출방법)

### ENDPOINT

| Method | endpoint | Request Header | Request Body | Remark |
|:------:|-------------|-----|------|--------|
|POST|/user/signup||name, nickname, email, password|회원가입|
|POST|/user/login||email, password|로그인|
|POST|/post/list|Authorization|title, body, category|게시물 작성|
|GET|/post/detail/<int:post_id>|Authorization, cookie||게시물 조회|
|DELETE|/post/detail/<int:post_id>|Authorization||게시물 삭제|
|PUT|/post/detail/<int:post_id>|Authorization|title, body, category|게시물 수정|
|GET|/post/list?page=|||게시물 목록 조회|
|GET|/post/list?category=|||게시물 카테고리 필터|


---

## API 명세(request/response)

### 1. 회원가입
- Method : POST
- EndpointURL : /user/signup
- Remark : (email : @와 .이 포함된 이메일 형식), (password : 8자리 이상. 숫자, 문자, 특수문자 포함)
- Request
```
POST "http://127.0.0.1:8000/user/signup HTTP/1.1"
{
    "name" : "muk",
    "nickname" : "muk",
    "email" : "muk@gmail.com",
    "password" : "mukmuk12!"
}
```
- Response
```
{
    "MESSAGE": "SUCCESS"
}
```

### 2. 로그인
- Method : POST
- EndpointURL : /user/login
- Remark : (email : @와 .이 포함된 이메일 형식), (password : 8자리 이상. 숫자, 문자, 특수문자 포함)
- Request
```
POST "http://127.0.0.1:8000/user/login HTTP/1.1"
{
    "email" : "muk@gamil.com",
    "password" : "mukmuk12!",
}
```
- Response
```
{
    "MESSAGE": "SUCCESS",
    "ACCESS_TOKEN": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NH0.ALnstfNp6Cbca2R26cWRnFnHEAlIrU9O5u4pZnRk2tY"
}
```

### 3. 게시물 
- Method : POST
- EndpointURL : /post/list
- Remark : 로그인한 유저만 게시글 작성 가능
- Request
```
POST "http://127.0.0.1:8000/posts HTTP/1.1"
{
    "title"   : "test게시글",
    "body" : "내용 test입니다",
    "category" : "자유게시판"
}
```
- Response
```
{
    "MESSAGE": "SUCCESS",
    }
}
```

### 4. 게시물 조회
- Method : GET
- EndpointURL : /posts/detail/<int:post_id>
- Request
```
GET "http://127.0.0.1:8000/posts/detail/1 HTTP/1.1"
```
- Response
```
{
    "Result": {
        "nickname": "muk1",
        "title": "1번 게시글",
        "hit": 1,
        "category": "자유게시판",
        "body": "1번 게시글 내용입니다",
        "created_at": "2021-10-19 01:59:27",
        "updated_at": "2021-10-19 01:59:27"
    },
    "Comment" : []
}
```

### 5. 게시물 수정
- Method : PUT
- EndpointURL : /post/detail/<int:post_id>
- Remark : 로그인한 유저가 본인의 게시물 수정 가능
- Request
```
PUT "http://127.0.0.1:8000/posts/detail/13 HTTP/1.1" 
{
   "title" : "test",
   "body" : "내용 수정test입니다",
   "category" : "팝니다"
}
```
- Response
```
{
    "MESSAGE": "SUCCESS"
}
```

### 6. 게시물 삭제
- Method : DELETE
- EndpointURL : /post/detail/<int:post_id>
- Remark : 로그인한 유저가 해당 게시물 삭제 가능
- Request
```
DELETE "http://127.0.0.1:8000/posts/detail/13 HTTP/1.1"
```
- Response
```
{
    "MESSAGE": "POST_DELETED"
}
```

### 7. 게시물 목록 조회
- Method : GET
- EndpointURL : /posts/list?page=
- Remark : 게시글 리스트 조회 기능, QueryParams(limit/offset)로 페이지네이션 가능
- Request
```
GET "http://127.0.0.1:8000/posts/list?page=1 HTTP/1.1"
```
- Response
```
{
    "Result": [
        {
            "count" : 1,
            "nickname": "muk1",
            "title": "1번 게시글",
            "body": "1번 게시글 내용입니다",
            "hit": 0
        },
        {
            "count" : 2,
            "nickname": "muk1",
            "title": "2번 게시글",
            "body": "2번 게시글 수정 내용입니다",
            "hit": 0
        },
        {
            "count" : 3,
            "nickname": "muk1",
            "title": "4번 게시글",
            "body": "4번 게시글 내용입니다",
            "hit": 0
        },
        {
            "count" : 4,
            "nickname": "muk1",
            "title": "5번 게시글",
            "body": "5번 게시글 내용입니다",
            "hit": 0
        },
        {
            "count" : 5,
            "nickname": "muk2",
            "title": "6번 게시글",
            "body": "6번 게시글 내용입니다",
            "hit": 0

        }
    ]
}
```
### 8. 게시물 카테고리 필터 조회
- Method : GET
- EndpointURL : /posts/list?category=
- Remark : 게시글 카테고리 필터 기능, QueryParams(limit/offset)로 페이지네이션 가능
- Request
```
GET "http://127.0.0.1:8000/posts/list?category=자유게시판 HTTP/1.1"
```
- Response
```
{
    "Result": [
        {
            "count" : 1,
            "nickname": "muk1",
            "title": "1번 게시글",
            "body": "1번 게시글 내용입니다",
            "hit": 0
        },
        {
            "count" : 2,
            "nickname": "muk1",
            "title": "2번 게시글",
            "body": "2번 게시글 수정 내용입니다",
            "hit": 0
        },
         {
            "count" : 3,
            "nickname": "muk1",
            "title": "5번 게시글",
            "body": "5번 게시글 내용입니다",
            "hit": 0
        }
   ]
}

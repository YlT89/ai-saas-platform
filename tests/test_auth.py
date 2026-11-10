def test_login_and_access_protected(client):
    """测试登录并获取 Token 访问受保护接口"""
    # 1. 先注册用户 (保证测试数据库里有这个账号)
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "Password123", "email": "test@example.com"}
    )

    # 2. 登录（注意你的登录接口是 form-data 格式）
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "Password123"}
    )
    assert login_response.status_code == 200, f"登录失败，状态码: {login_response.status_code}"
    token = login_response.json()["access_token"]

    # 3. 带着 Token 访问受保护接口
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/user/me", headers=headers)
    assert me_response.status_code == 200
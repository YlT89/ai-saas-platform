def test_read_main(client):
    """测试根路径是否能正常访问"""
    response = client.get("/")
    assert response.status_code == 200
    # 根据你的实际返回内容断言
    # assert response.json() == {"msg": "项目启动成功了，访问 /docs 调试接口"}

def test_stream_endpoint(client):
    """测试流式接口"""
    response = client.get("/stream")
    assert response.status_code == 200
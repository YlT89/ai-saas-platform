import redis, json

r = redis.Redis(host='localhost', port=6380, decode_responses=True)

print("=" * 50)
print("【Keyspace 概览】")
print(r.info('keyspace'))

for db in [0, 1]:
    r2 = redis.Redis(host='localhost', port=6380, db=db, decode_responses=True)
    keys = r2.keys('*')
    print(f"\n【{db} 号库】共 {len(keys)} 个 key")
    for k in keys[:20]:
        t = r2.type(k)
        print(f"  {k}  ({t})")

print("\n" + "=" * 50)
print("【向量索引列表】")
try:
    idx = r.execute_command('FT._LIST')
    print(idx if idx else "❌ 没有任何向量索引（文档未入库）")
except Exception as e:
    print(f"❌ 查询失败: {e}")

print("\n【Redis 模块】")
mods = r.module_list()
print([m['name'] for m in mods] if mods else "❌ 无模块（缺 RediSearch）")
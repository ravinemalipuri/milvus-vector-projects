from pymilvus import connections, utility

connections.connect(host="localhost", port="19530")
print("Connected! Milvus version:", utility.get_server_version())

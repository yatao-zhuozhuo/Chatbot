import dashscope
from dashscope import TextEmbedding
from dashvector import Client, Doc
import json

dashscope.api_key = ''

# 初始化 DashVector client
client = Client(
    api_key='', #此api为向量库api，不要搞错
    endpoint=''
)
def prepare_data(path, size):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for i in range(0, len(data), size):
                yield data[i:i + size]
    except Exception as e:
        print(f"Error preparing data from {path}: {e}")
        raise

def generate_embeddings(text):
    try:
        rsp = TextEmbedding.call(model=TextEmbedding.Models.text_embedding_v1, input=text)
        embeddings = [record['embedding'] for record in rsp.output['embeddings']]
        return embeddings if isinstance(text, list) else embeddings[0]
    except Exception as e:
        print(f"Error generating embeddings for text: {e}")
        raise



def get_embeddings(json_path):
    with open('../process_data/num.txt', 'r', encoding='utf-8') as file:
        num = int(file.read())
    # 尝试获取集合并处理错误
    try:
        collection = client.get('HCI_collection')
        if not collection:
            raise Exception("Failed to get collection")
    except Exception as e:
        print(f"Error getting collection: {e}")
        exit(1)

    sum=0
    batch_size = 10
    for docs in prepare_data(json_path, batch_size):
        try:
            print(f"Processing batch of size {len(docs)}")
            sum=len(docs)
            # 批量 embedding
            embeddings = generate_embeddings([doc['title'] for doc in docs])
            print(f"Generated embeddings for batch")

            # 批量写入数据
            rsp = collection.insert(
                [
                    Doc(id=str(index + num), vector=embedding, fields={"title": doc['title']})
                    for index, (doc, embedding) in enumerate(zip(docs, embeddings))
                ]
            )
            if not rsp:
                raise Exception("Failed to insert documents")
            print(f"Inserted batch into collection")
        except Exception as e:
            print(f"Error inserting documents: {e}")
            break

    with open('../process_data/num.txt', 'w', encoding='utf-8') as file:
        file.write(str(num+sum))

    
    #删除answer.json和answers.json的内容
    history1=[]
    history1.append({'title':''})
    with open('../process_data/answer.json', 'w') as json_file:
        json.dump(history1, json_file, ensure_ascii=False, indent=4)

    history=[]
    history.append({'role': 'assistant', 'content':''})

    with open('../process_data/answers.json', 'w', encoding='utf-8') as json_file:
        json.dump(history, json_file, ensure_ascii=False, indent=4)








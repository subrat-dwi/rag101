from index import index
from retrieve import generate_response
from server import app
import uvicorn

def main():

    uvicorn.run(app, host="0.0.0.0", port=8000)

    
    # while True:
    #     query = input("Me: ")
    #     if query.lower() == "exit":
    #         break
    #     response = generate_response(query)
    #     print(f"\nCutie: {response.choices[0].message.content}\n")




if __name__ == "__main__":
    main()
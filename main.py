from index import index
from retrieve import generate_response

def main():

    index()
    
    while True:
        query = input("Me: ")
        if query.lower() == "exit":
            break
        response = generate_response(query)
        print(f"Cutie: {response.choices[0].message.content}\n")


if __name__ == "__main__":
    main()
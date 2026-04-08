from index import load_pdf, split_documents, embed_documents

def main():
    file_path = "data_files/The_Courage_to_be_Disliked_How_to_Change_Your_Life_and_Achieve_Real.pdf"
    documents = load_pdf(file_path)
    print(f"Loaded {len(documents)} documents from the PDF.")

    chunks = split_documents(documents)
    print(f"Split the documents into {len(chunks)} chunks.")

    embed_documents(chunks)
    print("Embedded the chunks and stored them in the vector store.")


if __name__ == "__main__":
    main()
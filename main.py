from index import load_pdf

def main():
    file_path = "data_files/The_Courage_to_be_Disliked_How_to_Change_Your_Life_and_Achieve_Real.pdf"
    documents = load_pdf(file_path)
    print(f"Loaded {len(documents)} documents from the PDF.")
    print(f"First document content: {documents[10].page_content[:500]}")  # Print the first 500 characters of the first document


if __name__ == "__main__":
    main()
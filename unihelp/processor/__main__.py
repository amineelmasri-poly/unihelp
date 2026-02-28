import argparse
import glob
import os
from .pipeline import DocumentPipeline

def main():
    parser = argparse.ArgumentParser(description="Process administrative documents into JSON chunks.")
    parser.add_argument("input", help="File or directory path to process")
    parser.add_argument("--output-dir", help="Directory to save output JSON files", default=".")
    
    args = parser.parse_args()
    
    pipeline = DocumentPipeline()
    
    # Process directory
    if os.path.isdir(args.input):
        files = glob.glob(os.path.join(args.input, "**", "*.*"), recursive=True)
        supported_exts = {".pdf", ".docx", ".xlsx", ".txt"}
        files_to_process = [f for f in files if os.path.splitext(f)[1].lower() in supported_exts]
        
        print(f"Found {len(files_to_process)} supported files in directory.")
        
        if not os.path.exists(args.output_dir) and args.output_dir != ".":
            os.makedirs(args.output_dir)
            
        for file in files_to_process:
            try:
                base_name = os.path.splitext(os.path.basename(file))[0]
                output_path = os.path.join(args.output_dir, f"{base_name}_processed.json")
                pipeline.process_and_save(file, output_path)
                print(f"Successfully processed: {file} -> {output_path}")
            except Exception as e:
                print(f"Failed to process {file}: {e}")
                
    # Process single file
    elif os.path.isfile(args.input):
        if not os.path.exists(args.output_dir) and args.output_dir != ".":
            os.makedirs(args.output_dir)
            
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        output_path = os.path.join(args.output_dir, f"{base_name}_processed.json")
        try:
            pipeline.process_and_save(args.input, output_path)
            print(f"Successfully processed: {args.input} -> {output_path}")
        except Exception as e:
            print(f"Failed to process {args.input}: {e}")
            
    else:
        print(f"Error: Invalid input path '{args.input}'")

if __name__ == "__main__":
    main()

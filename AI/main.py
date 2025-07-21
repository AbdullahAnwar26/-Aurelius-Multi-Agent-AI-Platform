from PIL import Image
import os

def sample_root_agent(query: str, file_path=None):
    
    sample_directory = "C:\\Users\\devra\\Desktop\\AI"  #enter your file path of the directory
    sample_image_path = os.path.join(sample_directory, "sample_image.png")
    output_filename = "sample_output.txt"                    #file output is optional, only certain agents return files. 
    sample_output = "sample text output of the root agent"   #text will always be one of the output 
    file_contents = "generated text of the output file"
    
    os.makedirs(sample_directory, exist_ok=True)
    
    output_filepath = os.path.join(sample_directory, output_filename)
    with open(output_filepath, 'w') as f:
        f.write(file_contents)
        
        
    # this image output is optional, only stock agent returns images 
    img = Image.open(sample_image_path)
    img.show()

    return sample_output, f"the sample file output is stored in {output_filepath}"

result = sample_root_agent("user query")  # text will always be a user query, sometimes files can also be input 
print(result)

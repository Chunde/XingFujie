import os

def add_prefix_to_specific_file(file_path, prefix):
    directory, filename = os.path.split(file_path)
    new_filename = f"{prefix}{filename}"
    new_file_path = os.path.join(directory, new_filename)
        # os.rename(file_path, new_file_path)
    return new_file_path
from littlefs import LittleFS

files = [
    'main.py',
]
output_image = 'littlefs.img'  # symlinked/copied to rp2040js root directory
lfs = LittleFS(block_size=4096, block_count=352, prog_size=256)
# lfs = LittleFS(block_size=512, block_count=256)

for filename in files:
    print(f"Saving {filename}")
    try:
      with open("python/" + filename, 'rb') as src_file, lfs.open(filename, 'w') as lfs_file:
          print(f"Saved {filename}")
          lfs_file.write(src_file.read().decode())
    except FileNotFoundError as e:
      print(f"Error: {e}")
      raise e
with open(output_image, 'wb') as fh:
    fh.write(lfs.context.buffer)

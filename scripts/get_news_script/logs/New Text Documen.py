with open("skipped_files.txt", "r") as f:
    lines = f.readlines()

print("Total skipped:", len(lines))
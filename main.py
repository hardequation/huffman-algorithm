import EncodeDecodeTools as edt

while True:
    chose = input("Input:\n - '1' for compressing file\n - '2' for decompressing file\n - '3' to exit\n Your choice: ")

    try:
        if chose == '1':
            file_name = input("Input file name: ")
            edt.to_zmh(file_name)
            print("Compressing is succesful! File was compressed to '" + file_name + ".zmh'")
        elif chose == '2':
            file_name = input("Input file name with .zmh extension: ")

            if not file_name.endswith('.zmh'):
                print("ERROR: File doesn't have 'zmh' extension")
                continue

            edt.from_zmh(file_name)
            print("Decompressing is succesful! File was decompressed to '" + file_name.split('.zmh')[0] + "'")
        elif chose == '3':
            print("Exit")
            break
        else:
            print("Error: Selected wrong parameter, try again")

    except FileNotFoundError:
        print("ERROR: Couldn't open file")

    except Exception:
        print("ERROR: We have problems...")

    print()



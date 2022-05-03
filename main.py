import EncodeDecodeTools as edt

file_name = "input"

edt.to_zmh(file_name)

edt.from_zmh(file_name + '.zmh')

# with open(file_name, "w") as f:
#     f.write("f"*100000)



confirmStart = raw_input("Test will take approximately n minutes. Is this okay? Enter Y/N: ")
print(confirmStart)
if confirmStart != "Y" and confirmStart != "N":
	confirmStart = raw_input("Invalid entry. Please reenter, Y/N: ")
	if confirmStart != "Y" and confirmStart != "N":
		print(" Invalid entry. Two strikes, you're out. Exiting program.")
		exit()
	elif confirmStart == "Y" or confirmStart == "N":
		pass
	pass
if confirmStart == "N":
	print("As you wish. Exiting program.")
	exit()
elif confirmStart == "Y":
	print("Okay, trudging right along.")

print("Here's the rest of the code")
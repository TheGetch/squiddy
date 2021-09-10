def clean(filename):
    blacklist = ["\\", "/", ":", "*", "?", '"', "<", ">", "|", "\0"]
    filename = "".join(c for c in filename if c not in blacklist)
    return (
        filename.rstrip(". ")
        .replace("..", "__")
        .replace("~", "__")
        .strip()
    )

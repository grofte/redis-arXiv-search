from pathlib import Path
import tarfile
import re
import json

tars = Path("./arxiv_src/").glob("arXiv_src*")

# If there are nested tags then this regex will fail - I think
equation = r"\\begin\{equation\}.*?\\end\{equation\}"
align = r"\\begin\{align}.*?\\end\{align\}"
align_star = r"\\begin\{align\*}.*?\\end\{align\*\}"

# Dictionary id: tex where id is the arXiv id of the paper and tex is a list of extracted equations in latex
id_tex = {}

total_files = 0
# This gives us way too many backslashes in the output. I think. Or the right amount.
for tar in tars:
    with tarfile.open(tar) as tar:
        for tarinfo in tar:
            total_files += 1
            if tarinfo.isreg() and tarinfo.name.endswith(".gz"):
                arxiv_id = tarinfo.name[5:-3]
                tex_snippets = []
                fp = tar.extractfile(tarinfo)
                # Some files can't be opened despite the .gz extension
                try:
                    with tarfile.open(fileobj=fp, mode="r:gz") as gz:
                        # print(tarinfo.name)
                        for gzinfo in gz:
                            if gzinfo.isreg() and gzinfo.name.endswith(".tex"):
                                # print(gzinfo.name)
                                tex = gz.extractfile(gzinfo).read().decode()
                                tex_snippets = tex_snippets + re.findall(
                                    "|".join([equation, align, align_star]), tex, re.S
                                )
                    id_tex[arxiv_id] = tex_snippets
                except:
                    pass

with open("./arxiv_src/id_tex.json", "w") as fp:
    json.dump(id_tex, fp, ensure_ascii=False, indent=4)

print("Total files processed:", total_files)
print("Total files with a .gz extension:", len(id_tex))
print(
    "Total files with equations extracted:", len({k: v for k, v in id_tex.items() if v})
)


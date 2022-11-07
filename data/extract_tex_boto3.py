# %%
# Python 3.9+
import boto3
import tarfile
import re
import json
import io


# AWS credentials are usually stored in ~/.aws/credentials or as environment variables
# arXiv data is stored in a requester pays S3 bucket so I think it is about $0.01-0.03 per GB
s3_bucket = boto3.resource("s3").Bucket("arxiv")
# Select a subset of the files to process - empty strings should mean all files
begins_with = "src/arXiv_src_20"
ends_with = "_001.tar"

# If there are nested tags then this regex will fail - I think
# If you don't want the begin and end tags saved then replace ".*?" with "(.*?)"
tex_tags = [
    r"\\begin\{equation\}.*?\\end\{equation\}",
    r"\\begin\{align}.*?\\end\{align\}",
    r"\\begin\{align\*}.*?\\end\{align\*\}",
]
# %%

total_files = 0
total_gz = 0
total_extracted = 0

for s3_object in s3_bucket.objects.filter(Prefix="src/", RequestPayer="requester"):
    if s3_object.key.startswith(begins_with) and s3_object.key.endswith(ends_with):
        # Dictionary id: tex where id is the arXiv id of the paper and tex is a list of extracted equations in latex
        id_tex = {}
        print(s3_object.key)
        tar = s3_object.get(RequestPayer="requester")["Body"].read()
        tar = io.BytesIO(tar)
        # This gives us way too many backslashes in the output. I think. Or the right amount.
        with tarfile.open(fileobj=tar) as tar:
            for tarinfo in tar:
                total_files += 1
                if tarinfo.isreg() and tarinfo.name.endswith(".gz"):
                    total_gz += 1
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
                                        "|".join(tex_tags), tex, re.S
                                    )
                        id_tex[arxiv_id] = tex_snippets
                    except:
                        pass

        with open(
            ".arxiv_src/"
            + s3_object.key.removeprefix("src/").removesuffix(".tar")
            + ".json",
            "w",
        ) as fp:
            json.dump(id_tex, fp, ensure_ascii=False, indent=4)
        total_extracted += len({k: v for k, v in id_tex.items() if v})

# %%

print("Total files processed:", total_files)
print("Total files with a .gz extension:", total_gz)
print("Total files with equations extracted:", total_extracted)

# %%

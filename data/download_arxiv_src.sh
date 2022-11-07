# To download all the source files from 2020 but only the first 500 MB from each month
aws s3 cp s3://arxiv/src/ ./arxiv_src --request-payer requester --recursive --exclude "*" --include "arXiv_src_20*_001.tar"

# To do the same but from 2019
aws s3 cp s3://arxiv/src/ ./arxiv_src --request-payer requester --recursive --exclude "*" --include "arXiv_src_19*_001.tar"

# To do the same but with all the files from December 2020
aws s3 cp s3://arxiv/src/ ./arxiv_src --request-payer requester --recursive --exclude "*" --include "arXiv_src_2012_*.tar"

# To do the same but with all the files from December 2019
aws s3 cp s3://arxiv/src/ ./arxiv_src --request-payer requester --recursive --exclude "*" --include "arXiv_src_1912_*.tar"

# Remember that you can use the --dryrun option to see what files will be downloaded
# NOTE: I don't know if that is actually true - just something Co-pilot suggested

# Remember that you have to pay for the data transfer
# https://aws.amazon.com/s3/pricing/ but probably 1 to 3 cent per GB

# Remember that --exclude "*" must come before --include "arXiv_src_20*_001.tar"

# Filter for only the metadata from 2020
cat arxiv-metadata-oai-snapshot.json  | grep '"id":"20' > 2020_arxiv-metadata-oai-snapshot.json

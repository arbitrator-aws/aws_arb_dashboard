# Arbitrage tracker
Built using Chalice
arbitrator-dashboard
    - 1st revision
arbitrator-dashboard-0.2
    - second rev
## venv
python3 -m venv /home/phil/vscode_proj/aws/aws_arb_dashboard/.env
source /home/phil/vscode_proj/aws/aws_arb_dashboard/.env/bin/activate

pip install chalice==1.13.1 Jinja2==2.11.1 requests==2.18.4

chalice new-project db_test && cd db_test

cd to env directory and:
chalice local
or 
chalice deploy
    - dont forget aws cli tool
# Layers
- only for first revision
## Wheels
declare -a wheels=("https://files.pythonhosted.org/packages/07/08/a549ba8b061005bb629b76adc000f3caaaf881028b963c2e18f811c6edc1/numpy-1.18.2-cp36-cp36m-manylinux1_x86_64.whl" \
"https://files.pythonhosted.org/packages/e7/f9/f0b53f88060247251bf481fa6ea62cd0d25bf1b11a87888e53ce5b7c8ad2/pytz-2019.3-py2.py3-none-any.whl" \
"https://files.pythonhosted.org/packages/bb/71/8f53bdbcbc67c912b888b40def255767e475402e9df64050019149b1a943/pandas-1.0.3-cp36-cp36m-manylinux1_x86_64.whl" \
"https://files.pythonhosted.org/packages/d4/70/d60450c3dd48ef87586924207ae8907090de0b306af2bce5d134d78615cb/python_dateutil-2.8.1-py2.py3-none-any.whl" \
"https://files.pythonhosted.org/packages/65/eb/1f97cb97bfc2390a276969c6fae16075da282f5058082d4cb10c6c5c1dba/six-1.14.0-py2.py3-none-any.whl" \
"https://files.pythonhosted.org/packages/27/24/4f35961e5c669e96f6559760042a55b9bcfcdb82b9bdb3c8753dbe042e35/Jinja2-2.11.1-py2.py3-none-any.whl" \
"https://files.pythonhosted.org/packages/b2/5f/23e0023be6bb885d00ffbefad2942bc51a620328ee910f64abe5a8d18dd1/MarkupSafe-1.1.1-cp36-cp36m-manylinux1_x86_64.whl" \
"https://files.pythonhosted.org/packages/cc/94/5f7079a0e00bd6863ef8f1da638721e9da21e5bacee597595b318f71d62e/Werkzeug-1.0.1-py2.py3-none-any.whl" \
"https://files.pythonhosted.org/packages/dd/c0/4d8f43a9b16e289f36478422031b8a63b54b6ac3b1ba605d602f10dd54d6/click-7.1.1-py2.py3-none-any.whl" \
"https://files.pythonhosted.org/packages/f2/28/2a03252dfb9ebf377f40fba6a7841b47083260bf8bd8e737b0c6952df83f/Flask-1.1.2-py2.py3-none-any.whl" \
"https://files.pythonhosted.org/packages/76/ae/44b03b253d6fade317f32c24d100b3b35c2239807046a4c953c7b89fa49e/itsdangerous-1.1.0-py2.py3-none-any.whl")

## download layer deps
for w in ${wheels[@]}; do
    wget -nc $w -P wheels/
done

## install contents in env
<!-- mkdir -p layers/collector_common/python/lib/python3.6/site-packages/ -->
for wheel in wheels/*; do
    pip install $wheel
done

## unzip contents
mkdir -p layers/arbitrator_dashboard_01/python/lib/python3.6/site-packages/
for wheel in layers/wheels/*; do
    unzip -o $wheel -d layers/arbitrator_dashboard_01/python/lib/python3.6/site-packages/
done

## Zip up the layer contents
## mkdir -p layers/zips

rm layers/zips/arbitrator_dashboard_01.zip
pushd layers/arbitrator_dashboard_01
zip -o -r -p ../zips/arbitrator_dashboard_01.zip python
popd

## push the layer
## source awsmfa xxxxx 
aws s3 sync layers/zips/ s3://arbitrator-store/lambda/layers/arbitrator_dashboard_01/ --delete

## Build/update layer absaoss-fraud-py36-np-pd-tfl
aws lambda publish-layer-version \
--layer-name arbitrator-dashboard \
--description "Python 3.6.9 layer: pydeps and dashboard test" \
--content S3Bucket=arbitrator-store,S3Key=lambda/layers/arbitrator_dashboard_01/arbitrator_dashboard_01.zip \
--compatible-runtimes python3.6


test
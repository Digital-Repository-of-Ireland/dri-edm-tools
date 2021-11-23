if ! [ $2 ];
then
    echo "Usage: ./add-isPartOf.sh <projectcode> <directory>"
    exit 1
fi

if ! [ -d $2 ];
then
    echo "Second parameter must be a directory"
    exit 1
fi

sed -i "s/<\/dc:title>/<\/dc:title><dcterms:isPartOf>$1<\/dcterms:isPartOf>/" $2/*.xml


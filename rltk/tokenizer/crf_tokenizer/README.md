# dig-crf-tokenizer

The tokenization rules take into account embedded HTML tags and
entities. HTML tags begin with "<" and end with ">". The contents of a
tag are treated as a single token, although internal spaces, tabs, and
newlines are stripped out so as not to confuse CRF++. HTML entities
begin with "&" and end with ";", with certain characters allowed
inbetween. They are treated as single tokens.

HTML tags and HTML entities optionally can be skipped (omitted form the
output array of tokens) after recognition.

There are risks to the HTML processing rules when the text being
tokenized is not proper HTML.  Left angle brackets can cause the
following text to become a single token.  Ampersands can merge into
the following textual word.

A possible solution to the bare ampersand problem is to recognize only
the defined set of HTML entities. It is harder to think of a solution
to the bare left angle bracket problem; perhaps check if they are
followed by the beginning of a valid HTML tag name?

There is also special provision to group contiguous punctuation characters.
The way to use this tokenizer is to create an instance of it, set any
processing flags you need, then call the tokenize(value) function,
which will return the tokens in an array.

To tokenize, breaking on punctuation without recognizing HTML tags and
entities, try:
```
t = CrfTokenizer()
tokens = t.tokenize(value)
```

To tokenize, breaking on punctuation and recognizing both HTML tags and
entites as special tokens, try:
```
t = CrfTokenizer()
t.setRecognizeHtmlEntities(True)
t.setRecognizeHtmlTags(True)
tokens = t.tokenize(value)
```

To tokenize, breaking on punctuation, recognizing and HTML tags and
entities, and skipping the tags, try:
```
t = CrfTokenizer()
t.setRecognizeHtmlEntities(True)
t.setRecognizeHtmlTags(True)
t.setSkipHtmlTags(True)
tokens = t.tokenize(value)
```

The following sequence will tokenize, strip HTML tags, then join the tokens
into a string.  The final result will be the input string with HTML entities
treated as single tokens, HTML tags stripped out, punctuation separated from
adjacent words, and excess white space removed.
```
t = CrfTokenizer()
t.setRecognizeHtmlEntities(True)
t.setRecognizeHtmlTags(True)
t.setSkipHtmlTags(True)
result = t.tokenize(value).join(" ")
```

The same as above, but with punctuation remaining glued to adjacent words:
```
t = CrfTokenizer()
t.setRecognizePunctuation(False)
t.setRecognizeHtmlTags(True)
t.setSkipHtmlTags(True)
result = t.tokenize(value).join(" ")
```

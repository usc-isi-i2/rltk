import string
import sys


class CrfTokenizer:
    """The tokenization rules take into account embedded HTML tags and
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

t = CrfTokenizer()
tokens = t.tokenize(value)

To tokenize, breaking on punctuation and recognizing both HTML tags and
entites as special tokens, try:

t = CrfTokenizer()
t.setRecognizeHtmlEntities(True)
t.setRecognizeHtmlTags(True)
tokens = t.tokenize(value)

To tokenize, breaking on punctuation, recognizing and HTML tags and
entities, and skipping the tags, try:

t = CrfTokenizer()
t.setRecognizeHtmlEntities(True)
t.setRecognizeHtmlTags(True)
t.setSkipHtmlTags(True)
tokens = t.tokenize(value)

The following sequence will tokenize, strip HTML tags, then join the tokens
into a string.  The final result will be the input string with HTML entities
treated as single tokens, HTML tags stripped out, punctuation separated from
adjacent words, and excess white space removed.

t = CrfTokenizer()
t.setRecognizeHtmlEntities(True)
t.setRecognizeHtmlTags(True)
t.setSkipHtmlTags(True)
result = t.tokenize(value).join(" ")

The same as above, but with punctuation remaining glued to adjacent words:

t = CrfTokenizer()
t.setRecognizePunctuation(False)
t.setRecognizeHtmlTags(True)
t.setSkipHtmlTags(True)
result = t.tokenize(value).join(" ")
    """

    whitespaceSet = set(string.whitespace)
    punctuationSet = set(string.punctuation)
    htmlEntityNameCharacterSet = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                                  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                                  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '#'}
    linebreaking_start_character_set = {'\n', '\r'}
    linebreaking_character_set = {'\n', '\r', '\t'}
    START_HTML_TAG_CHAR = "<"
    END_HTML_TAG_CHAR = ">"
    START_HTML_ENTITY_CHAR = "&"
    END_HTML_ENTITY_CHAR = ";"

    def __init__(self, recognize_linebreaks=False, skipHtmlTags=False, skipHtmlEntities=False,
                 recognizePunctuation=True, recognizeHtmlTags=False, recognizeHtmlEntities=False,
                 groupPunctuation=False, create_structured_tokens=False):
        self.groupPunctuation = groupPunctuation
        self.recognizeHtmlEntities = recognizeHtmlEntities
        self.recognizeHtmlTags = recognizeHtmlTags
        self.recognizePunctuation = recognizePunctuation  # Notice
        self.skipHtmlEntities = skipHtmlEntities
        self.skipHtmlTags = skipHtmlTags
        self.tokenPrefix = None
        self.recognize_linebreaks = recognize_linebreaks
        self.create_structured_tokens = create_structured_tokens

    def setGroupPunctuation(self, groupPunctuation):
        """When True and self.recognizePunctuation is True, group adjacent punctuation
        characters into a token.

        """
        self.groupPunctuation = groupPunctuation

    def setRecognizeHtmlEntities(self, recognizeHtmlEntities):
        """When True, assume that the text being parsed is HTML.  Recognize HTML
        entities, such as "&gt;", and parse them into single tokens (e.g.,
        "&gt;" instead of ["&", "gt", ";"]).

        """
        self.recognizeHtmlEntities = recognizeHtmlEntities

    def setRecognizeHtmlTags(self, recognizeHtmlTags):
        """When True, assume that the text being parsed is HTML.  Recognize HTML tags,
        such as "<bold>", and parse them into single tokens (e.g., "<bold>"
        instead of ["<", "bold", ">"]).

        """
        self.recognizeHtmlTags = recognizeHtmlTags

    def setRecognizePunctuation(self, recognizePunctuation):
        """When True, treat punctuation characters as separate tokens.

        """
        self.recognizePunctuation = recognizePunctuation

    def setSkipHtmlEntities(self, skipHtmlEntities):
        """When True and when self.recognizeHtmlEntities is True, skip HTML entities instead of storing them as tokens.

        """
        self.skipHtmlEntities = skipHtmlEntities

    def setSkipHtmlTags(self, skipHtmlTags):
        """When True and when self.recognizeHtmlTags is True, skip HTML tags instead
        of storing them as tokens.

        """
        self.skipHtmlTags = skipHtmlTags

    def setTokenPrefix(self, tokenPrefix):
        """When non None, a string that should be prepended to each token. This may be
        useful when tokens are being generated from different sources, and it
        is desired to be able to distinguish the source of a token.

        """
        self.tokenPrefix = tokenPrefix

    def setRecognizeLinebreaks(self, recognize_linebreaks):
        """When True line breaks \n and \r will be recognized as tokens and all line
        breaking characters will be grouped into a single token.

        """
        self.recognize_linebreaks = recognize_linebreaks

    def tokenize(self, value):
        """Take a string and break it into tokens. Return the tokens as a list of
        strings.

        """

        # This code uses a state machine:
        class STATE:
            NORMAL = 0
            GROUP_PUNCTUATION = 1
            PROCESS_HTML_TAG = 2
            PROCESS_HTML_ENTITY = 3
            GROUP_LINEBREAKS = 4

        state_names = {
            STATE.NORMAL: "normal",
            STATE.GROUP_PUNCTUATION: "punctuation",
            STATE.PROCESS_HTML_TAG: "html",
            STATE.PROCESS_HTML_ENTITY: "html_entity",
            STATE.GROUP_LINEBREAKS: "break"
        }

        # "state" and "token" have array values to allow their
        # contents to be modified within finishToken().
        state = [STATE.NORMAL]
        token = [""]  # The current token being assembled.
        tokens = []  # The tokens extracted from the input.
        index = -1

        def clearToken():
            """Clear the current token and return to normal state."""
            token[0] = ""
            state[0] = STATE.NORMAL

        def emitToken():
            """Emit the current token, if any, and return to normal state."""
            if len(token[0]) > 0:
                # add character end and start
                char_start, char_end = index, index + len(token[0])
                if self.create_structured_tokens:
                    new_token = {'value': token[0], 'type': state_names[state[0]], 'char_start': char_start,
                                 'char_end': char_end}
                    tokens.append(new_token)
                else:
                    tokens.append(token[0])
            clearToken()

        def fixBrokenHtmlEntity():
            # This is not a valid HTML entity.
            # TODO: embedded "#" characters should be treated better
            # here.
            if not self.recognizePunctuation:
                # If we aren't treating punctuation specially, then just treat
                # the broken HTML entity as an ordinary token.
                #
                # TODO: This is not quite correct.  "x& " should
                # be treated as a single token, althouth "s & "
                # should result in two tokens.
                state[0] = STATE.NORMAL
                return
            if self.groupPunctuation:
                # If all the saved tokens are punctuation characters, then
                # enter STATE.GROUP_PUNCTUATION insted of STATE.NORMAL.
                sawOnlyPunctuation = True
                for c in token[0]:
                    if c not in CrfTokenizer.punctuationSet:
                        sawOnlyPunctuation = False
                        break
                if sawOnlyPunctuation:
                    state[0] = STATE.GROUP_PUNCTUATION
                    return

            # Emit the ampersand that began the prospective entity and use the
            # rest as a new current token.
            saveToken = token[0]
            token[0] = saveToken[0:1]
            emitToken()
            if len(saveToken) > 1:
                token[0] = saveToken[1:]
                # The caller should continue processing with the current
                # character.

        # Process each character in the input string:
        for c in value:
            index += 1
            if state[0] == STATE.PROCESS_HTML_TAG:
                if c in CrfTokenizer.whitespaceSet:
                    continue  # Suppress for safety. CRF++ doesn't like spaces in tokens, for example.
                token[0] += c
                if c == CrfTokenizer.END_HTML_TAG_CHAR:
                    if self.skipHtmlTags:
                        clearToken()
                    else:
                        emitToken()
                continue

            if state[0] == STATE.PROCESS_HTML_ENTITY:
                # Parse an HTML entity name. TODO: embedded "#"
                # characters imply more extensive parsing rules should
                # be performed here.
                if c == CrfTokenizer.END_HTML_ENTITY_CHAR:
                    if len(token[0]) == 1:
                        # This is the special case of "&;", which is not a
                        # valid HTML entity.  If self.groupPunctuation is
                        # True, return to normal parsing state in case more
                        # punctuation follows.  Otherwise, emit "&" and ";" as
                        # separate tokens.
                        if not self.recognizePunctuation:
                            # TODO: This is not quite correct.  "x&;" should
                            # be treated as a single token, althouth "s &;"
                            # should result in two tokens.
                            token[0] = token[0] + c
                            state[0] = STATE.NORMAL
                        elif self.groupPunctuation:
                            token[0] = token[0] + c
                            state[0] = STATE.GROUP_PUNCTUATION
                        else:
                            emitToken()  # Emit the "&" as a seperate token.
                            token[0] = token[0] + c
                            emitToken()  # Emit the ";' as a seperate token.
                        continue
                    token[0] = token[0] + c
                    if self.skipHtmlEntities:
                        clearToken()
                    else:
                        emitToken()
                    continue
                elif c in CrfTokenizer.htmlEntityNameCharacterSet:
                    token[0] = token[0] + c
                    continue
                else:
                    # This is not a valid HTML entity.
                    fixBrokenHtmlEntity()
                    # intentional fall-through

            if state[0] == STATE.GROUP_LINEBREAKS:
                # we will look for \n\r and ignore spaces
                if c in CrfTokenizer.linebreaking_character_set:
                    token[0] += c
                    continue
                elif c in CrfTokenizer.whitespaceSet:
                    continue
                else:
                    emitToken()
                    state[0] = STATE.NORMAL

            if c in CrfTokenizer.whitespaceSet:
                # White space terminates the current token, then is dropped.
                emitToken()
                # Check to see whether we should look for line breaks
                if c in CrfTokenizer.linebreaking_start_character_set and self.recognize_linebreaks:
                    state[0] = STATE.GROUP_LINEBREAKS
                    token[0] = c

            elif c == CrfTokenizer.START_HTML_TAG_CHAR and self.recognizeHtmlTags:
                emitToken()
                state[0] = STATE.PROCESS_HTML_TAG
                token[0] = c

            elif c == CrfTokenizer.START_HTML_ENTITY_CHAR and self.recognizeHtmlEntities:
                emitToken()
                state[0] = STATE.PROCESS_HTML_ENTITY
                token[0] = c

            elif c in CrfTokenizer.punctuationSet and self.recognizePunctuation:
                if self.groupPunctuation:
                    # Finish any current token.  Concatenate
                    # contiguous punctuation into a single token:
                    if state[0] != STATE.GROUP_PUNCTUATION:
                        emitToken()
                        state[0] = STATE.GROUP_PUNCTUATION
                    token[0] = token[0] + c
                else:
                    # Finish any current token and form a token from
                    # the punctuation character:
                    emitToken()
                    token[0] = c
                    emitToken()

            else:
                # Everything else goes here. Presumably, that includes
                # Unicode characters that aren't ASCII
                # strings. Further work is needed.
                if state[0] != STATE.NORMAL:
                    emitToken()
                token[0] = token[0] + c

        # Finish any final token and return the array of tokens:
        if state[0] == STATE.PROCESS_HTML_ENTITY:
            fixBrokenHtmlEntity()
        emitToken()

        # Was a token prefix requested? If so, we'll apply it now.  If the
        # normal case is not to apply a token prefix, this might be a little
        # more efficient than applying the prefix in emitToken().
        if self.tokenPrefix is not None and len(self.tokenPrefix) > 0:
            tokens = map(lambda x: self.tokenPrefix + x, tokens)

        return tokens


class ngramTokenizer(CrfTokenizer):
    place_holder = '#'

    def __init__(self):
        CrfTokenizer.__init__(self)
        self.token_string = ""
        # self.ngrams = set()

    def transform(self, token_list):
        self.token_string = ngramTokenizer.place_holder.join(token_list)

    def basic(self, input_string, q):
        ngrams = set()
        token_list = CrfTokenizer.tokenize(self, input_string)
        self.transform(token_list)
        last_pos = len(self.token_string) - q + 1
        for i in range(last_pos):
            ngrams.add(self.token_string[i:i + q])
        return ngrams

    def positional(self, input_string, q):
        ngrams = set()
        token_list = CrfTokenizer.tokenize(self, input_string)
        self.transform(token_list)
        last_pos = len(self.token_string) - q + 1
        for i in range(last_pos):
            ngrams.add(self.token_string[i:i + q] + str(i))
        return ngrams

    def padded(self, input_string, q):
        ngrams = set()
        token_list = CrfTokenizer.tokenize(self, input_string)
        self.transform(token_list)
        self.token_string = ngramTokenizer.place_holder * (q - 1) + self.token_string + ngramTokenizer.place_holder * (
        q - 1)
        last_pos = len(self.token_string) - q + 1
        for i in range(last_pos):
            ngrams.add(self.token_string[i:i + q])
        return ngrams


def main(argv=None):
    '''this is called if run from command line'''

    t = CrfTokenizer()
    print(t.tokenize("This is a sentence."))
    print(t.tokenize("Buy???This...Now!!!"))
    print(t.tokenize("The <bold>only</bold> source."))
    print(t.tokenize("The<bold>only</bold>source."))
    print(t.tokenize("Big&gt;little."))
    print(t.tokenize("Big & little."))
    print(t.tokenize("blond&curly."))
    print(t.tokenize("&brokenHtml"))
    t.setGroupPunctuation(True)
    t.setRecognizeHtmlTags(True)
    t.setRecognizeHtmlEntities(True)
    print(t.tokenize("Buy???This...Now!!!"))
    print(t.tokenize("The <bold>only</bold> source."))
    print(t.tokenize("The<bold>only</bold>source."))
    print(t.tokenize("Big&gt;little."))
    print(t.tokenize("Big & little."))
    print(t.tokenize("blond&curly."))
    print(t.tokenize("&brokenHtml"))
    t.setSkipHtmlTags(True)
    t.setSkipHtmlEntities(True)
    print(t.tokenize("Buy???This...Now!!!"))
    print(t.tokenize("The <bold>only</bold> source."))
    print(t.tokenize("The<bold>only</bold>source."))
    print(t.tokenize("Big&gt;little."))
    print(t.tokenize("Big & little."))
    print(t.tokenize("blond&curly."))
    print(t.tokenize("&brokenHtml"))
    t.setTokenPrefix("X:")
    print(t.tokenize("Tokenize with prefixes."))
    t.setTokenPrefix(None)
    print(t.tokenize("No more  prefixes."))
    t.setRecognizePunctuation(False)
    print(t.tokenize("This is a sentence."))
    print(t.tokenize("Buy???This...Now!!!"))
    print(t.tokenize("The <bold>only</bold> source."))
    print(t.tokenize("The<bold>only</bold>source."))
    print(t.tokenize("Big&gt;little."))
    print(t.tokenize("Big & little."))
    print(t.tokenize("blond&curly."))
    print(t.tokenize("&brokenHtml"))
    print(t.tokenize("A line break goes here\n\t \rand a new line starts"))
    t.setRecognizeLinebreaks(True)
    print(t.tokenize("A line break goes here\n\r \rand a new line starts"))

    nt = ngramTokenizer()
    print('\nNGRAM tokeniser\n')
    print(nt.basic("Pablo Picasso Jr.", 2))
    print(nt.positional("Pablo Picasso Jr.", 2))
    print(nt.padded("Pablo Picasso Jr.", 2))


# call main() if this is run as standalone
if __name__ == "__main__":
    sys.exit(main())

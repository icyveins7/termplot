# Why not use rich?

I did some initial testing for a typical `imagesc` or `imshow` implementation, where the end result would require two steps:

1. Generate a colored 'space' for each pixel.
2. Stitch all colored pixels together into one long text string.

In `rich`, this amounts to something like:

```python
from rich.text import Text
from rich.style import Style

t = [Text(" ",style=Style(bgcolor=f"rgb({i[0]},{i[1]},{i[2]})")) for i in colors]
tl = Text.assemble(*t)
# This appears to take 34.7ms on my Macbook Air M1
```

The equivalent for `termcolor` would be something like:

```python
from termcolor import colored

t = [colored(" ", None, c) for c in colors]
tl = "".join(t)
# This appears to take 4.12ms on my Macbook Air M1
```

Not sure why there's such a big difference, but I'll probably stick to termcolor for now, until I really need all of `rich`'s bells and whistles.

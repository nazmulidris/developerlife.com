---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---
# Sample heading 1
This is sample text

## Sample code
```kotlin
#!/usr/bin/env kscript
//DEPS com.squareup.okhttp3:okhttp:3.11.0

import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.URLEncoder

val arg = when {
    args.size > 0 -> args[0]
    else -> "https://en.wikipedia.org/wiki/Cache_replacement_policies#Last_in_first_out_(LIFO)"
}

val encodedData = URLEncoder.encode(arg, "UTF-8")
val url = "https://tinyurl.com/api-create.php?url=$encodedData"

print(doGet(url))

fun doGet(url: String): String {
    val request = Request.Builder().url(url).build()
    val response = OkHttpClient().newCall(request).execute()
    return response.body()!!.string()
}
```

### Other stuff
- Item 1
- Item 2

### Images

- How to insert SVG images?
---
layout:     post
title:      Post 3
date:       2018-07-29 13:35:54 -0700
categories: cat1 cat2 cat3
---
# ~~Heading 1~~
Don't use `#` in your posts ... this will look smaller than `##`. The post title already uses
`<h1>` and you're only supposed to have one of them on a page (HTML semantic best practices).

## Heading 2
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been 
the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley 
of type and scrambled it to make a type specimen book. 

### Heading 3
It has survived not only five centuries, but also the leap into electronic typesetting, 
remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset 
sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like 
Aldus PageMaker including versions of Lorem Ipsum.

{% highlight kotlin %}
import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.URLEncoder

val arg = when {
    args.size > 0 -> args[0]
    else -> "https://en.wikipedia.org/wiki/Cache_replacement_policies#Last_in_first_out_(LIFO)"
}
{% endhighlight %}

```kotlin
val encodedData = URLEncoder.encode(arg, "UTF-8")
val url = "https://tinyurl.com/api-create.php?url=$encodedData"

print(doGet(url))

fun doGet(url: String): String {
    val request = Request.Builder().url(url).build()
    val response = OkHttpClient().newCall(request).execute()
    return response.body()!!.string()
}
```

```java
String a = String.valueOf(2); 
int i = Integer.parseInt(a);  
BufferedWriter out = null;
try {
    out = new BufferedWriter(new FileWriter("filename", true));
    out.write("aString");
} catch (IOException e) {
    // error processing code
} finally {
    if (out != null) {
        out.close();
    }
}
```

### Heading 3
It has survived not only five centuries, but also the leap into electronic typesetting, 
remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset 
sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like 
Aldus PageMaker including versions of Lorem Ipsum.

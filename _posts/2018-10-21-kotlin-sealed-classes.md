---
author: Nazmul Idris
date: 2018-10-21 5:00:00+00:00
excerpt: |
  This tutorial is an exploration of Kotlin sealed classes and how they can be used to represent
  state elegantly and robustly
layout: post
title: "Kotlin Sealed Classes and State"
categories:
  - State
  - KT
---

<img class="post-hero-image" src="{{ 'assets/kotlin-awesomeness-hero.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Sealed classes and state](#sealed-classes-and-state)
- [Example 1 - Android permissions](#example-1---android-permissions)
- [Example 2 - Android GMS Tasks API](#example-2---android-gms-tasks-api)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Sealed classes and state

Kotlin sealed classes are like enums with super powers. They can be used to concisely and elegantly
represent state information. They can be use in finite state machines as well (eg via Redux) but
this tutorial will only explore how they can be used to represent state in some common problems you
encounter in Android development.

Please watch [this great video](https://www.youtube.com/watch?v=uGMm3StjqLI) on Kotlin sealed
classes and state management by
[Patrick Cousins](https://www.linkedin.com/in/patrick-cousins-530117127) which was recorded during
KotlinConf 2018.

## Example 1 - Android permissions

If an Android app requires
[dangerous permissions](https://developer.android.com/guide/topics/permissions/overview#dangerous-permission-prompt)
then it becomes necessary to prompt the end user of the app to grant such permissions. This requires
quite a bit of back and forth, and in most cases, an Activity has to be extended in order to provide
an implementation of `onRequestPermissionsResult()`. Also, the Activity itself is needed to make the
permission request.

So here's the overall flow of what has to happen.

1.  The Activity's `requestPermissions(Activity, Array<String>< Int)` method has to be called in
    order to display the permissions prompt to the end user.

1.  The Activity's `onRequestPermissionsResult(Int, Array<String>, IntArray)` method has to be
    overridden in order to determine if the user pressed pressed the "ALLOW" or "DENY" button when
    presented w/ the prompt to grant the permission at runtime.

        1. If the permission was granted, then the operation that required the permission can be
        performed.

        1. If the permission was denied, then let the user know that the app requires this permission
        in order to function (or whatever makes sense for your app).

In order to determine whether the permission was granted or not, requires a lengthy if statement to
interpret the meaning of the 3 parameters of the `onRequestPermissionsResult()`. And this is where
sealed classes can make life much simpler by turning these 3 objects into a simple expression of
what the state of the approval is. The following is an example of what this might look like.

```kotlin
sealed class PermissionResult {
    class Granted(id: Int) : PermissionResult()
    class Revoked(id: Int) : PermissionResult()
    class Cancelled(id: Int) : PermissionResult()

    companion object {
        fun convert(requestCode: Int,
                    permissions: Array<String>,
                    grantResults: IntArray): PermissionResult {
            return when {
                // If request is cancelled, the result arrays are empty.
                grantResults.isEmpty() -> Cancelled(requestCode)
                // Permission was granted, 🎉. Run the pending task function.
                grantResults.first() == PERMISSION_GRANTED -> Granted(requestCode)
                // Permission denied, ☹.
                else -> Revoked(requestCode)
            }
        }
    }
}
```

And here's an example of using this in the Activity.

```kotlin
class DriverActivity : AppCompatActivity() {

    override fun onRequestPermissionsResult(requestCode: Int,
                                            permissions: Array<String>,
                                            grantResults: IntArray) {
        PermissionsHandler.onRequestPermissionsResult(
            requestCode, permissions, grantResults)
    }

}
```

Here's the implementation of the method that the Activity calls to figure out what happened w/ the
permission grant from the user.

```kotlin
fun onRequestPermissionsResult(requestCode: Int,
                               permissions: Array<String>,
                               grantResults: IntArray) {
    when (requestCode) {
        PERMISSION_ID -> {
            when (PermissionResult.convert(requestCode, permissions, grantResults)) {
                is PermissionsHandler.PermissionResult.Granted -> {
                    if (pendingTask != null) {
                        "🔒 Permission is granted 🙌, Execute pendingTask".log()
                        pendingTask?.onPermissionGranted()
                        pendingTask = null
                    }
                }
                is PermissionsHandler.PermissionResult.Revoked -> {
                    pendingTask?.onPermissionRevoked()
                }
                is PermissionsHandler.PermissionResult.Cancelled -> {

                }
            }
        }
        // Add other 'when' lines to check for other permissions this app might request.
        else -> {
            // Ignore all other requests.
        }
    }
}
```

Finally, here's the code block that kicks it all off (when the Activity requests a permission).

```kotlin
fun executeTaskOnPermissionGranted(context: AppCompatActivity,
                                   task: PermissionDependentTask) {
    if (isPermissionDenied(context,
                           task.getRequiredPermission())) {
        // Permission is not granted ☹. Ask the user for the run time permission 🙏.
        "🔒 ${task.getRequiredPermission()} not granted 🛑, request it 🙏️".log()
        requestPermission(context,
                          task.getRequiredPermission(),
                          PERMISSION_ID)
        if (pendingTask == null) pendingTask = task
    } else {
        // Permission is granted 🙌. Run the task function.
        "🔒 ${task.getRequiredPermission()} permission granted 🙌, run task ".log()
        task.onPermissionGranted()
    }
}
```

And here's where the call to `executeTaskOnPermissionGranted()` occurs in a part of the app that
requires a permission in order to continue.

```kotlin
executeTaskOnPermissionGranted(
    object : PermissionDependentTask {
        override fun getRequiredPermission() =
                android.Manifest.permission.ACCESS_FINE_LOCATION

        override fun onPermissionGranted() {
            serviceGetCurrentPlace.execute()
            snack(fragmentContainer) {
                setText(R.string.message_making_api_call_getCurrentPlace)
            }

        }

        override fun onPermissionRevoked() {
            snack(fragmentContainer) {
                setText(resources.getString(
                        R.string.message_permission_missing_for_api_call,
                        getRequiredPermission()))
                duration = Snackbar.LENGTH_LONG
            }
        }
    })
```

For a complete listing of sources in a real world example that uses this please checkout the
following links.

1. [Permissions.kt](https://github.com/nazmulidris/places-api-poc/blob/main/app/src/main/kotlin/com/google/api/places/places_api_poc/misc/Permissions.kt)
1. [DriverActivity.kt](https://github.com/nazmulidris/places-api-poc/blob/main/app/src/main/kotlin/com/google/api/places/places_api_poc/ui/DriverActivity.kt)

> Here's a link to the [repo](https://github.com/nazmulidris/places-api-poc/) for this project.

## Example 2 - Android GMS Tasks API

Google Play Services uses the [Tasks API](https://developers.google.com/android/guides/tasks) in
order to provide an implementation of "promises" for asynchronous operations. It can be quite
tedious to wade through the generics, and interfaces, and ceremony that this API requires. While
understandable, why it has such complexity, the use of sealed classes and [extension function
expressions]({{ '/2018/10/20/kotlin-extension-function-expressions/' | relative_url }}) can make
using this API a breeze.

Here's the flow that occurs when using the Task API.

1. There's a service that can be accessed via some client object. This client object is created and
   some arguments are passed to it, in order to get some results from it. This is the gist of the
   service request and response. However, the service might take some arbitrary amount of time to
   provide the result, and instead of awaiting the results, this is where Task API comes into play.
   The service client provides a Task object when the request is made. Also, keep in mind that the
   result might be an error.

1. In order to do something when the Task actually has results, a lambda / closure / higher order
   function has to be provided to the Task (that was created above) so that when it completes with a
   success or error, then this result can be used to do something that's useful for the app.

From the perspective of the code that uses the Task, what would really be nice is an error or a
result back from the response. Please note that the request is created by the client w/ the
arguments passed to the client. Here's what this response might look like, using Kotlin sealed
classes.

```kotlin
sealed class ServiceResponse<T> {
    data class Success<T>(val value: T) : ServiceResponse<T>()
    data class Error<T>(val exception: Exception) : ServiceResponse<T>()
}
```

Leveraging extension function expressions on the Task API, we get.

```kotlin
fun <T> Task<T>.handleResponse(executorService: ExecutorService,
                               functor: (ServiceResponse<T>) -> Unit) {
    addOnCompleteListener(
            executorService,
            OnCompleteListener<T> {
                // This runs in a background thread (provided by the executor).
                if (isSuccessful && result != null) {
                    functor(ServiceResponse.Success(result!!))
                } else {
                    functor(ServiceResponse.Error(exception!!))
                }
            }
    )
}
```

Here's an example of how this could be used.

```kotlin
currentLocationClient.lastLocation
        .handleResponse(executorWrapper.executor) { response ->
            when (response) {
                is ServiceResponse.Success -> {
                    processCurrentLocation(response.value)
                }
                is ServiceResponse.Error -> {
                    "⚠️ Task failed with exception ${response.exception}".log()
                }
            }

        }
```

Here's another example.

```kotlin
currentPlaceClient.getCurrentPlace(null)
        .handleResponse(executorWrapper.executor) { response ->
            when (response) {
                is ServiceResponse.Success -> {
                    processPlacelikelihoodBuffer(response.value)
                    response.value.release()
                }
                is ServiceResponse.Error -> {
                    "⚠️ Task failed with exception ${response.exception}".log()
                }
            }
        }
```

> Here's a link to the
> [repo](https://github.com/nazmulidris/places-api-poc/tree/main/app/src/main/kotlin/com/google/api/places/places_api_poc/service)
> for this project where you can find all the classes in the `service` package that leverage this
> sealed class and this extension function expression.

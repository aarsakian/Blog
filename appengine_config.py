# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START vendor]
from google.appengine.ext import vendor
vendor.add('lib')
#see issue https://github.com/jschneier/django-storages/issues/281
import tempfile # gae version
import tempfile2

tempfile.SpooledTemporaryFile = tempfile2.SpooledTemporaryFile



# Add any libraries installed in the "lib" folder.


# [END vendor]

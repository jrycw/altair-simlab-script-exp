# altair-simlab-script-exp
## Why this repo
This repo is an experiment to see if there are different approaches to writing the SimLab script.

## Current Approach (given by the tutorial)
### Procedure
1. Firstly, you need to use the `macro` function to record the operation you would like to transfer as a script.
2. Then extract the template that describes the operation in `xml` format from the script.
3. Replace the `xml` value, text,...or whatever you would like to treat as the variables, and then inject the hardcoded values.
4. Finally, call `simlab.execute` to perform the operation.

The final code would be something like the following:
```python
from hwx import simlab


RenameBody ="""<RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
      <Model>$Geometry</Model>
      <Body>"Body 2",</Body>
    </Entities>
    </SupportEntities>
    <NewName Value="CH"/>
    <Output/>
    </RenameBody>"""
simlab.execute(RenameBody)
```
### Problem
Though the given approach works well, manually injecting the hardcoded value and then directly sending the template to execute doesn't sound right to me.
This approach has some drawbacks, in my opinion:
* The template only suits the current problem, which makes it difficult to reuse.
* What if you want to perform similar operations? What will you do? From my understanding, the tutorial suggests duplicating the template as many times as we need, which means you'll have `RenameBody1`, `RenameBody2`...`RenameBodyn`. Meanwhile, since it is extremely error-prone, you need to be very careful to examine the injected values and texts in EVERY SINGLE RenameBody before executing, that's not trivial work.
* What's worse? How to share the scripts with other developers? Everyone has `RenameBody1`...`RenameBodyn` in every project, and every `RenameBody` only suits their own needs.


### Sub-optimal approach
Maybe we could try to abstract the template as a function, so we might end up having:
```python
from hwx import simlab


def rename_body(model_text, body_text, newname_value):
    return """<RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
    <Model>""" + model_text + """</Model>
    <Body>""" + body_text + """</Body>
    </Entities>
    </SupportEntities>
    <NewName Value=""" + newname_value + """/>
    <Output/>
    </RenameBody>"""
RenameBody = rename_body("$Geometry", '"Body 2",' '"CH"')
simlab.execute(RenameBody)
```
Well, this solution kind of solves the problem. But what if we have a template with 100 lines, and each line contains something we would like to extract as the parameters (the mesh control config, the mesh quality criteria config...etc), etc.)? What will you do? Manually doing this is definitely another nightmare.

## My experimental approach
### Procedure
Could we figure out a way to dynamically extract the `xml` values and texts where we are mostly interested in? Yes, programming can do anything!!! But how could this be possible?

I've come up with the following idea:
1. Utilize the `xml` module to build the tree system from a given template.
2. Construct a sector of code to extract the `xml` values and texts as the parameters, but in string format.
3. Then use `exec` to execute the sector of code. Now, we have a function that is generated at runtime (let's call it `get_tree`).
4. We're able to call `get_tree` like `get_tree()` or `get_tree(NewNameValue="NewName", BodyText='"Body 9",', ModelText="$AnotherGeoIsOk")` to retrieve the tree system.
5. Finally, we create a function (let's call it `get_template`) to transform the tree system into `xml` format, which is ready to be fed to SimLab to execute.

### Step by step
1. Build `_get_base_template` and `get_base_template`.
2. Organize the template as an iterator.
3. Start to loop over the iterator and collect the parsed string.
4. Call `exec(code)`.
5. Build `get_template`.

#### 1. Build `_get_base_template` and `get_base_template`
* `_get_base_template` serves an internal implementation, which can be obtained from
    * directly return the string in `xml` format.
    * manually-saved template in the disk or via a local API call.
    * official API call from Altair in the future, if provided.
*  `get_template` serves a public interface, which is basically a wrapper for  `_get_base_template`. By using this technique, the public interface won't be influenced by the detailed implementation of the template if future changes happen.
```python
def _get_base_template():
    return """<RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
      <Model>$Geometry</Model>
      <Body>"Body 2",</Body>
    </Entities>
    </SupportEntities>
    <NewName Value="CH"/>
    <Output/>
    </RenameBody>"""
    
def get_base_template():
    return _get_base_template()

base_template = get_base_template()
```

#### 2. Organize the template as an iterator
* Utilize `xml` module to read the template and then collect every tag, attrib and text in a namedtuple named Row as an iterator.
```python
import xml.etree.ElementTree as ET
from collections import namedtuple


def process_data(base_template):
    root = ET.fromstring(base_template)
    Row = namedtuple('Row', 'tag attrib text')
    return (Row(child.tag, child.attrib, child.text)
            for child in root.iter())

data = process_data(base_template)
```

#### 3. Start to loop over the iterator and collect the parsed string
* Define a variable called `code_str` to accumulate the parsed string.
* Here we hardcode the function name as `get_tree`, which accepts an arbitrary number of keyword-only arguments.
```python
code_str = "def get_tree(**kwargs):\n"
```

##### Root element
* Since the first Row instance must be the root element, we can directly parse it through `parse_root_elem`, which calls `create_root_elem` to create the root element. The root element is hardcoded as `rootx` for now. Note that `PADS4` is needed for the purpose of indentation, since we're literally creating a function in string format.
```python
PADS4 = " "*4


def create_root_elem(child):
    return PADS4 + f"rootx = ET.Element('{child.tag}', {child.attrib})\n"

def parse_root_elem(code_str, child):
    return code_str + create_root_elem(child)

code_str = parse_root_elem(code_str, next(data))
```
##### Other elements
* Next, we start to loop over the iterator to deal with two kinds of elements: one is w/o subelement (top element) and the other one is w/ subelement (grouped element). If `child.text` is `None`,  we categorize it as the top element. If its `child.tag` is equal to some predefined name,  we categorize it as the grouped element. In our demo template, there's only one grouped element, and its tag is `SupportEntities`. Note that we need to remember to call `append_return` at the end to complete the function.
```python
while True:
    try:
        child = next(data)
    except StopIteration:
        break
    else:
        if child.text is None:  # top element
            code_str = parse_top_elem(code_str, child)
        # Grouped element(need other elif to expand other groups)
        elif child.tag == "SupportEntities":
            code_str = parse_supportentities(data, code_str, child)
        else:  # Not grouped element and with child.text
            pass

code_str += append_return()
```
###### Top element
* Firstly, we create the top element and then check if `child.attrib` exists or not. If `child.attrib` exists, we need to perform `inject_pseudo_value` to do some tricks. You might notice that there are some `\`s to escape `''` and some `\n`s as the line break, which looks not pretty but is unavoidable since we're making the function in string format anyway.
    *  We create a `pseudo` variable to be a placeholder for the value of this top element as its tag plus `Value`(I know the naming rule is not pythonic, but I chose it for certain reasons...). For instance, if the `child.tag` is `NewName`, then we're expecting we can use `get_tree` like `get_tree(NewNameValue='NewNameYouWant')`. 
    * Then we try to use `kwargs.get` to see if we can get the user-given keyword-only argument, that is basically the `pseudo` placeholder. If the user is not given this keyword-only argument, we fallback to the default, child.attrib['Value']`, which is just the same as what we read.
    *  Next we are finally able to **inject** the `pseudo` back to `child.attrib['Value']`. 
* For the top element text, we need to inject the text to `None` if `child.text` is `None`. 
* After everything is well-prepared, we call `append_to_root` to append this top element back to `root` tree system.
* Finally, collect all the strings as the return value.

```python
def create_top_elem(child):
    return PADS4 + f"{child.tag} = ET.Element('{child.tag}', {child.attrib})\n"

def inject_pseudo_value(child):
    pseudo = f'{child.tag}Value'
    str_a = PADS4 + \
        f"pseudo = kwargs.get(\'{pseudo}\', \'{child.attrib['Value']}\')\n"
    str_b = PADS4 + f"{child.tag}.attrib['Value'] = pseudo\n"
    return str_a + str_b

def append_to_root(child):
    return PADS4 + f"rootx.append({child.tag})\n"

def parse_top_elem(code_str, child):
    sec_str1 = create_top_elem(child)
    if child.attrib:
        sec_str1 += inject_pseudo_value(child)

    sec_str2 = ""
    if child.text is None:
        sec_str2 += PADS4 + f"{child.tag}.text = None\n"

    sec_str3 = append_to_root(child)
    return code_str + sec_str1 + sec_str2 + sec_str3
```
###### Grouped element
* For the grouped element, we pretty much do the same operation as the top element. However, there's one thing to be noted: remember, you need to create the element or subelement first, and then you're able to inject since injection is like modifying something already existing. I knew it might sound trivial to you, but it's something I forgot all the time while formulating the `code_str`. **To sum up, the injection timing matters and should be considered thoroughly**.
* The trick here to handle subelements is to use `next(child)` to get the next child in the iterator.
* Note in this case, we need to call `inject_pseudo_text` instead of `inject_pseudo_value`. The injected operation should allow us to call `get_tree` like `get_tree(ModelText="$AnotherGeoIsOk")`.  

```python
def create_sub_elem(child, future_child):
    return PADS4 + f"{future_child.tag} = ET.SubElement({child.tag}, '{future_child.tag}', {future_child.attrib})\n"

def inject_pseudo_text(child):
    pseudo = f'{child.tag}Text'
    str_a = PADS4 + f"pseudo = kwargs.get(\'{pseudo}\', \'{child.text}\')\n"
    str_b = PADS4 + f"{child.tag}.text = pseudo\n"
    return str_a + str_b

def parse_supportentities(data, code_str, child):
    """
    <SupportEntities>
      <Entities>
        <Model>$Geometry</Model>
        <Body>"Body 2",</Body>
      </Entities>
    """
    # SupportEntities
    sec_str1 = create_top_elem(child) + append_to_root(child)

    # Entities
    second_child = next(data)
    sec_str2 = create_sub_elem(child, second_child)

    # Model
    third_child = next(data)
    sec_str3 = create_sub_elem(second_child, third_child)
    if third_child.text:
        sec_str3 += inject_pseudo_text(third_child)

    # Body
    fourth_child = next(data)
    # Noted that first one is second_child instead of third_chid
    sec_str4 = create_sub_elem(second_child, fourth_child)
    if fourth_child.text:
        sec_str4 += inject_pseudo_text(fourth_child)

    return code_str + sec_str1 + sec_str2 + sec_str3 + sec_str4
```
#### 4. Call `exec(code_str)`
* This one line will turn the code_str into a function (`get_tree`) we can call.
```python
exec(code_str)
```
#### 5. Build `get_template`
* `get_template` has nothing fancy but to write the tree system as `xml` format.
```python
import io


def get_template(rootx):
    tree = ET.ElementTree(rootx)
    dummy_file = io.BytesIO()
    tree.write(dummy_file)
    return dummy_file.getvalue().decode("utf-8")
```

## Concluding Remarks
* Regarding to what `xml` is actually helping us, you could refer to this [Linkedin post](https://www.linkedin.com/posts/driscollis_python-ugcPost-7055733050474729472-Kp38), written by `Michael Driscoll`.
* For your reference, if you're doing:
```python
rootx = get_tree(NewNameValue="NewName",
                 BodyText='"Body 9",',
                 ModelText="$AnotherGeoIsOk")
```
Then `exec(code_str)` is equivalent to defining a function dynamically in the global scope as below:
```python
def get_tree(**kwargs):    
    rootx = ET.Element('RenameBody', {'CheckBox': 'ON', 'UUID': '78633e0d-3d2f-4e9a-b075-7bff122772d8'})    
    
    SupportEntities = ET.Element('SupportEntities', {})    
    rootx.append(SupportEntities)    
    
    Entities = ET.SubElement(SupportEntities, 'Entities', {})    
    
    Model = ET.SubElement(Entities, 'Model', {})    
    pseudo = kwargs.get('ModelText', '$Geometry')    
    Model.text = pseudo    
    
    Body = ET.SubElement(Entities, 'Body', {})    
    pseudo = kwargs.get('BodyText', '"Body 2",')    
    Body.text = pseudo    
    
    NewName = ET.Element('NewName', {'Value': 'CH'})    
    pseudo = kwargs.get('NewNameValue', 'CH')    
    NewName.attrib['Value'] = pseudo    
    NewName.text = None    
    rootx.append(NewName)    
    
    Output = ET.Element('Output', {})    
    Output.text = None    
    rootx.append(Output)    
    return rootx'
```

## TODOs
Obviously, there are so many things we can do better in the code. For example:
1. Consider encapsulating the while-loop in the function. Maybe metaclass would be another good idea, since the magic dunder methods are quite helpful `__new__`, `__call__`, `__init__`).
2. Have a more elegant way to handle the grouped elements. In this code, we distinguish it by using an "elif". That's not good. What if we have multiple grouped elements? Maybe we could try using a recursive approach.
3. What if there are more than 1 subelement with the same tag, like we have 2 `Model` and 2 `Body`. How to name it? Maybe we need a `full-path` tag name like `EntitiesModelNewNameValue`.
4. Currently, if you give the wrong input, the code will be silent and not warn you. Maybe we should provide an `invalid input` warning and do nothing.

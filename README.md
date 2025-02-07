# FluentAssertions to xUnit Converter 🚀

This repository contains a Python script that automates the conversion of asserts written with **FluentAssertions** to the **xUnit** format in C# projects.  
This is especially useful when migrating projects to different unit testing frameworks without having to manually modify the code.

---

## 📋 Features

- Converts common asserts like `.Should().Be()`, `.Should().NotBeNull()`, `.Should().BeEquivalentTo()`, and more.
- Converts exception validations, HTTP status codes, and collections.
- Processes multiple `.cs` files automatically.

---

## 🛠️ Requirements

- **Python 3.6+** installed on your machine.
- A C# project using FluentAssertions with `.cs` files ready for conversion.

---

## 🚀 How to Use

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/FluentAssertionsToXUnitConverter.git
   cd FluentAssertionsToXUnitConverter
   ```

2. **Run the conversion script:**
   ```bash
   python fluent_to_xunit.py
   ```

3. **Provide the directory of your C# project:**
   The script will prompt you to enter the path to the directory containing the `.cs` files to be converted.

---

## 📄 Supported Patterns

### Assert conversions included in the script:

| FluentAssertions (Before)   | xUnit (After)                 |
|-----------------------------|-------------------------------|
| `.Should().Be(value)`       | `Assert.Equal(expected, actual)` |
| `.Should().NotBeNull()`     | `Assert.NotNull(actual)`      |
| `.Should().Throw<Exception>()` | `Assert.Throws<Exception>(() => ...)` |
| `.Should().Contain(item)`   | `Assert.Contains(item, collection)` |
| `.Should().BeEquivalentTo()` | `Assert.Equal(expected, actual)` |
| `.Should().Be200Ok()`       | `Assert.Equal(HttpStatusCode.OK, response.StatusCode)` |
| `.Should().BeNullOrEmpty()` | `Assert.True(content == null || !content.Any())` |

---

## 🔧 Customization

The `fluent_to_xunit.py` file contains a list of **regex patterns** and **replacements** that you can modify to fit your project’s specific needs.

Example pattern in the script:
```python
# .Should().Be(value) -> Assert.Equal(expected, actual)
(r'([\w\.\(\)]+)\.Should\(\)\.Be\((.*?)\);', r'Assert.Equal(\2, \1);')
```

If you need to add new patterns, simply follow the format above.

---

## 📁 Repository Structure

```
📂 FluentAssertionsToXUnitConverter
│
├── fluent_to_xunit.py        # Main conversion script
├── README.md                 # Documentation
```

---

## ⚠️ Considerations

- **Backup:** Before running the script, make a backup of your project or use a version control system like **Git** to avoid losing any changes.
- **Manual Review:** After the conversion, review the converted asserts to ensure they work correctly in the tests.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributions

Contributions are welcome! Feel free to open **issues** or submit **pull requests** with improvements.

---

💻 **Developed with 💙 by [Leticia Kawamoto](https://github.com/leticiasassaki).**

import re
import os

def migrate_fluent_to_xunit(file_path):
    """
    Migrates Fluent Assertions methods to xUnit assertions in a C# file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Patterns and replacements
    patterns = [
        # .ForEach(item => item.Prop.Should().BeTrue()); -> .ForEach(item => Assert.True(item.Prop));
        (r'([\w\.\(\)\?\[\]]+)\.ForEach\(\s*(\w+)\s*=>\s*\2\.([\w\.]+)\.Should\(\)\.BeTrue\(\)\s*\);', r'\1.ForEach(\2 => Assert.True(\2.\3));'),
        
        # .ForEach(item => item.Prop.Should().BeFalse()); -> .ForEach(item => Assert.False(item.Prop));
        (r'([\w\.\(\)\?\[\]]+)\.ForEach\(\s*(\w+)\s*=>\s*\2\.([\w\.]+)\.Should\(\)\.BeFalse\(\)\s*\);', r'\1.ForEach(\2 => Assert.False(\2.\3));'),

        # .ForEach(item => item.Prop.Should().Be(true)); -> .ForEach(item => Assert.True(item.Prop));
        (r'([\w\.\(\)\?\[\]]+)\.ForEach\(\s*(\w+)\s*=>\s*\2\.([\w\.]+)\.Should\(\)\.Be\(true\)\s*\);', r'\1.ForEach(\2 => Assert.True(\2.\3));'),

        # .ForEach(item => item.Prop.Should().Be(value)); -> .ForEach(item => Assert.Equal(value, item.Prop));
        (r'([\w\.\(\)\?\[\]]+)\.ForEach\(\s*(\w+)\s*=>\s*\2\.([\w\.]+)\.Should\(\)\.Be\((.*?)\)\s*\);', r'\1.ForEach(\2 => Assert.Equal(\4, \2.\3));'),

        # .ForEach(item => item.Prop.Should().BeNullOrEmpty()); -> .ForEach(item => Assert.True(string.IsNullOrEmpty(item.Prop)));
        (r'([\w\.\(\)\?\[\]]+)\.ForEach\(\s*(\w+)\s*=>\s*\2\.([\w\.]+)\.Should\(\)\.BeNullOrEmpty\(\)\s*\);', r'\1.ForEach(\2 => Assert.True(string.IsNullOrEmpty(\2.\3)));'),

        # .Should().Be(value) -> Assert.Equal(expected, actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be\((.*?)\);', r'Assert.Equal(\2, \1);'),

        # .Should().BeTrue() -> Assert.True(actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.BeTrue\(\);', r'Assert.True(\1);'),

        # .Should().BeFalse() -> Assert.False(actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.BeFalse\(\);', r'Assert.False(\1);'),

        # .Should().BeNull() -> Assert.Null(actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.BeNull\(\);', r'Assert.Null(\1);'),

        # .Should().NotBeNull() -> Assert.NotNull(actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.NotBeNull\(\);', r'Assert.NotNull(\1);'),
        
        # .Should().BeEmpty() -> Assert.Empty(value)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.BeEmpty\(\);', r'Assert.Empty(\1);'),

        # .Should().NotBe(Guid.Empty) -> Assert.NotEqual(Guid.Empty, value)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.NotBe\(Guid\.Empty\);', r'Assert.NotEqual(Guid.Empty, \1);'),

        # .Should().NotBe(value) -> Assert.NotEqual(expected, actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.NotBe\((.*?)\);', r'Assert.NotEqual(\2, \1);'),

        # Id.Should().NotBeEmpty() -> Assert.NotEqual(Guid.Empty, guid)
        (r'([\w\.]+\.Id)\.Should\(\)\.NotBeEmpty\(\);', r'Assert.NotEqual(Guid.Empty, \1);'),

        # .Should().NotBeEmpty() -> Assert.NotEmpty(collection)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.NotBeEmpty\(\);', r'Assert.NotEmpty(\1);'),

        # .Should().Contain(lambda) -> Assert.Contains(collection, lambda)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Contain\(\s*(\w+\s*=>.+?)\s*\);', r'Assert.Contains(\1, \2);'),

        # .Should().Contain(item) -> Assert.Contains(item, collection)
        (r'(.+?)\.Should\(\)\.Contain\((.+?)\);', r'Assert.Contains(\2, \1);'),

        # .Should().ContainSingle(predicate) -> Assert.Single(collection, predicate)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.ContainSingle\((.*?)\);', r'Assert.Single(\1, \2);'),

        # .Should().NotContain(item) -> Assert.DoesNotContain(item, collection)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.NotContain\((.*?)\);', r'Assert.DoesNotContain(\2, \1);'),

        # .Should().Throw<Exception>() -> Assert.Throws<Exception>(() => action)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Throw<(.+?)>\(\);', r'Assert.Throws<\2>(() => \1);'),

        # .Should().StartWith(value) -> Assert.StartsWith(value, actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.StartWith\((.*?)\);', r'Assert.StartsWith(\2, \1);'),

        # .Should().EndWith(value) -> Assert.EndsWith(value, actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.EndWith\((.*?)\);', r'Assert.EndsWith(\2, \1);'),

        # .Should().Be200Ok() -> Assert.Equal(HttpStatusCode.OK, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be200Ok\(\);', r'Assert.Equal(HttpStatusCode.OK, \1.StatusCode);'),

        # .Should().Be400BadRequest() -> Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be400BadRequest\(\);', r'Assert.Equal(HttpStatusCode.BadRequest, \1.StatusCode);'),

        # .Should().Be201Created() -> Assert.Equal(HttpStatusCode.Created, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be201Created\(\);', r'Assert.Equal(HttpStatusCode.Created, \1.StatusCode);'),

        # .Should().Be500InternalServerError() -> Assert.Equal(HttpStatusCode.InternalServerError, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be500InternalServerError\(\);', r'Assert.Equal(HttpStatusCode.InternalServerError, \1.StatusCode);'),

        # .Should().Be401Unauthorized() -> Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be401Unauthorized\(\);', r'Assert.Equal(HttpStatusCode.Unauthorized, \1.StatusCode);'),

        # .Should().Be403Forbidden() -> Assert.Equal(HttpStatusCode.Forbidden, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be403Forbidden\(\);', r'Assert.Equal(HttpStatusCode.Forbidden, \1.StatusCode);'),

        # .Should().Be404NotFound() -> Assert.Equal(HttpStatusCode.NotFound, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be404NotFound\(\);', r'Assert.Equal(HttpStatusCode.NotFound, \1.StatusCode);'),

        # .Should().SatisfyRespectively(...) -> Assert.Collection(...)
        (
            r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.SatisfyRespectively\((.*?)\);',
            r'Assert.Collection(\1, \2);'
        ),

        # .Should().BeGreaterThanOrEqualTo(value) -> Assert.True(actual >= value)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.BeGreaterThanOrEqualTo\((.*?)\);', r'Assert.True(\1 >= \2);'),

        # .Should().Be201Created() -> Assert.Equal(HttpStatusCode.Created, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be201Created\(\);', r'Assert.Equal(HttpStatusCode.Created, \1.StatusCode);'),

        # .Should().Be404NotFound() -> Assert.Equal(HttpStatusCode.NotFound, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be404NotFound\(\);', r'Assert.Equal(HttpStatusCode.NotFound, \1.StatusCode);'),

        # .Should().Be401Unauthorized() -> Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.Be401Unauthorized\(\);', r'Assert.Equal(HttpStatusCode.Unauthorized, \1.StatusCode);'),
        
        # .Should().BeEquivalentTo() -> Assert.Equal(expected, actual)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.BeEquivalentTo\((.*?)\);', r'Assert.Equal(\2, \1);'),
        
        # .Should().ThrowAsync<Exception>() -> await Assert.ThrowsAsync<Exception>(action)
        (r'await\s+([\w\.\(\)\?\[\]]+)\.Should\(\)\.ThrowAsync<([\w\d_\.]+)>\(\);', r'await Assert.ThrowsAsync<\2>(\1);'),

        # .Should().ThrowAsync<Exception>() -> await Assert.ThrowsAsync<Exception>(() => act)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.ThrowAsync<(.+?)>\(\)\s*\.WithMessage\((.*?)\);',  r'var exception = await Assert.ThrowsAsync<\2>(\1);\nAssert.Equal(\3, exception.Message);'),
        
        # .Should().BeNullOrEmpty() -> Assert.True(content == null || !content.Any())
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.BeNullOrEmpty\(\);', r'Assert.True(\1 == null || !\1.Any());'),

        # .Should().NotBeNullOrEmpty() -> Assert.NotNull(value); Assert.NotEmpty(value);
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.NotBeNullOrEmpty\(\);', r'Assert.NotEmpty(\1);'),

        # .Should().BeOfType<Type>() -> Assert.IsType<Type>(value)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.BeOfType<([\w\d_\.]+)>\(\);', r'Assert.IsType<\2>(\1);'),

        # .Should().HaveCount(number) -> Assert.Equal(number, value.Count)
        (r'([\w\.\(\)\?\[\]]+)\.Should\(\)\.HaveCount\((.*?)\);', r'Assert.Equal(\2, \1.Count);'),
    ]

    # Apply patterns to content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Save the modified content to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f'Migration completed for: {file_path}')


def process_directory(directory):
    """
    Processes all .cs files in a directory.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.cs'):
                file_path = os.path.join(root, file)
                migrate_fluent_to_xunit(file_path)


# Run the script in a directory
if __name__ == "__main__":
    directory_path = input("Enter the directory containing C# files: ").strip()
    if os.path.exists(directory_path):
        process_directory(directory_path)
    else:
        print("Directory not found!")

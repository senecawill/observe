To implement a feature that displays a message box indicating which field failed validation, we need to enhance the `FieldValidator` protocol and ensure that each form can handle displaying an error message. Here's how you can update your code:

1. **Enhance the `FieldValidator` Protocol**: Ensure that the validator not only returns a boolean but also provides a message if validation fails.
2. **Modify Validation Logic**: Update the logic to gather all failed fields and their messages.
3. **Display Error Messages**: Use an alert or custom view to display these errors.

Let's start by modifying the `FieldValidator` protocol and then update the `ViewControllerWT` class to handle displaying the error messages.

### Step 1: Enhance the `FieldValidator` Protocol

First, modify the `FieldValidator` protocol to return a tuple indicating whether validation passed and an optional message if it failed:

```swift
protocol FieldValidator {
    func validate(_ value: String) -> (Bool, String?)
}
```

### Step 2: Modify Validation Logic in `ViewControllerWT`

Next, update the `ViewControllerWT` class to gather all failed fields and their messages. We'll also add a method to display an alert with these errors.

```swift
import UIKit

class ViewControllerWT: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource {
    
    var nextControlYPosition: CGFloat = 0
    var nextControlTag: Int = 1000
    var pickerData: [Int: [String]] = [:]
    var timePickers: [UIDatePicker: UITextField] = [:]
    var scrollView: UIScrollView!
    var fieldsWithValidators: [(UIControl, FieldValidator)] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Initialize the scroll view
        scrollView = UIScrollView(frame: self.view.bounds)
        scrollView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        self.view.addSubview(scrollView)
        
        // Register for keyboard notifications
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillShow(notification:)), name: UIResponder.keyboardWillShowNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillHide(notification:)), name: UIResponder.keyboardWillHideNotification, object: nil)
    }
    
    func createTextField(name: String, textColor: UIColor? = nil, font: UIFont? = nil, validator: FieldValidator? = nil) -> UITextField {
        let textField = createField(name: name, control: UITextField(), validator: validator)
        textField.borderStyle = .roundedRect
        textField.backgroundColor = UIColor.systemBackground
        textField.layer.borderColor = UIColor.systemGray3.cgColor
        textField.layer.borderWidth = 0.25
        textField.keyboardType = .numberPad
        
        if let textColor = textColor {
            textField.textColor = textColor
        } else {
            textField.textColor = UIColor.label
        }

        if let font = font {
            textField.font = font
        } else {
            textField.font = UIFont.preferredFont(forTextStyle: .body)
        }
        
        return textField
    }
    
    // ... (other createField methods remain the same, but ensure they call `createField` with the validator parameter)

    private func createField<T: UIControl>(name: String, control: T, validator: FieldValidator? = nil) -> T {
        let labelWidth: CGFloat = 180
        let fieldWidth: CGFloat = view.frame.width - 32 - labelWidth
        let yPosition = nextControlYPosition
        
        let label = UILabel()
        label.text = name
        label.font = .systemFont(ofSize: 14)
        
        if T.self == UITextView.self || T.self == UIPickerView.self {
            label.frame = CGRect(x: 16, y: yPosition, width: view.frame.width - 32, height: 20)
        } else {
            label.frame = CGRect(x: 16, y: yPosition, width: labelWidth, height: 20)
        }
        scrollView.addSubview(label)
        
        control.addTarget(self, action: #selector(fieldDidChangeValue), for: .editingChanged)
        if let validator = validator {
            fieldsWithValidators.append((control, validator))
        }
        
        if T.self == UITextView.self || T.self == UIPickerView.self {
            control.frame = CGRect(x: 16, y: yPosition + 25, width: view.frame.width - 32, height: 30)
        } else {
            control.frame = CGRect(x: 16 + labelWidth, y: yPosition, width: fieldWidth, height: 30)
        }
        
        if let textView = control as? UITextView {
            control.frame.size.height = 100
            textView.layer.borderColor = UIColor.gray.cgColor
            textView.layer.borderWidth = 1.0
            textView.layer.cornerRadius = 5.0
            textView.isScrollEnabled = false
        }
        
        if let datePicker = control as? UIDatePicker {
            datePicker.datePickerMode = .date
        }
        
        scrollView.addSubview(control)
        nextControlYPosition += 40
        
        return control
    }

    @objc func fieldDidChangeValue(_ sender: UIControl) {

    }
    
    // ... (other methods remain the same)

    func validateFields() -> Bool {
        var errors: [(String, String)] = []
        
        for (field, validator) in fieldsWithValidators {
            guard let textField = field as? UITextField else { continue }
            let validationResult = validator.validate(textField.text ?? "")
            if !validationResult.0 {
                errors.append((textField.placeholder ?? "Unknown Field", validationResult.1 ?? "Validation failed"))
            }
        }
        
        if !errors.isEmpty {
            displayValidationError(errors)
            return false
        }
        
        return true
    }

    func displayValidationError(_ errors: [(String, String)]) {
        let errorMessages = errors.map { "\($0): \($1)" }.joined(separator: "\n")
        
        let alert = UIAlertController(title: "Validation Errors", message: errorMessages, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default, handler: nil))
        present(alert, animated: true, completion: nil)
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self, name: UIResponder.keyboardWillShowNotification, object: nil)
        NotificationCenter.default.removeObserver(self, name: UIResponder.keyboardWillHideNotification, object: nil)
    }
}
```

### Step 3: Update `FieldValidator` Implementations

Ensure that all your field validators return a tuple with the validation result and an error message if necessary. Here's an example of how you might update one:

```swift
class RequiredFieldValidator: FieldValidator {
    func validate(_ value: String) -> (Bool, String?) {
        if value.isEmpty {
            return (false, "This field is required.")
        }
        return (true, nil)
    }
}

class EmailFieldValidator: FieldValidator {
    func validate(_ value: String) -> (Bool, String?) {
        let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        let emailPredicate = NSPredicate(format:"SELF MATCHES %@", emailRegEx)
        if !emailPredicate.evaluate(with: value) {
            return (false, "Please enter a valid email address.")
        }
        return (true, nil)
    }
}
```

### Step 4: Call Validation

Whenever you need to validate the fields (e.g., before submitting a form), call `validateFields()` on your `ViewControllerWT` instance. If validation fails, it will display an alert with the errors.

```swift
@objc func submitButtonTapped(_ sender: UIButton) {
    if validateFields() {
        // Proceed with form submission
    } else {
        // Validation failed; error messages are already displayed.
    }
}
```

By following these steps, you ensure that all forms using `ViewControllerWT` will display validation errors in a user-friendly manner.
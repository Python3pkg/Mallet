#! /bin/bash

# Usage.
function usage {
    echo -e "Usage:"
    echo -e "$0 <dir>"
}

# Check parameters.
if [[ "$1" == "" || ! -d "$1" ]]; then
    usage
    exit 1
fi

# Files to copy
CPY=(
    "CFNetwork.framework/NSURLRequest.json"
    "CFNetwork.framework/NSURLRequestInternal.json"

    "QuartzCore.framework/CALayer.json"

    "StoreKit.framework/SKDownload.json"
    "StoreKit.framework/SKPayment.json"
    "StoreKit.framework/SKPaymentInternal.json"
    "StoreKit.framework/SKPaymentQueue.json"
    "StoreKit.framework/SKPaymentQueueInternal.json"
    "StoreKit.framework/SKPaymentTransaction.json"
    "StoreKit.framework/SKPaymentTransactionInternal.json"
    "StoreKit.framework/SKProduct.json"
    "StoreKit.framework/SKProductInternal.json"
    "StoreKit.framework/SKProductsRequest.json"
    "StoreKit.framework/SKProductsRequestInternal.json"
    "StoreKit.framework/SKProductsResponse.json"
    "StoreKit.framework/SKProductsResponseInternal.json"
    "StoreKit.framework/SKReceiptRefreshRequest.json"
    "StoreKit.framework/SKRequest.json"
    "StoreKit.framework/SKRequestInternal.json"

    "UIKit.framework/_UIDatePickerView.json"
    "UIKit.framework/UIAlertView.json"
    "UIKit.framework/UIButton.json"
    "UIKit.framework/UIControl.json"
    "UIKit.framework/UIDatePicker.json"
    "UIKit.framework/UILabel.json"
    "UIKit.framework/UIPageControl.json"
    "UIKit.framework/UIPickerView.json"
    "UIKit.framework/UIProgressView.json"
    "UIKit.framework/UIResponder.json"
    "UIKit.framework/UIScreen.json"
    "UIKit.framework/UIScrollView.json"
    "UIKit.framework/UISegmentedControl.json"
    "UIKit.framework/UISlider.json"
    "UIKit.framework/UIStepper.json"
    "UIKit.framework/UISwitch.json"
    "UIKit.framework/UITextField.json"
    "UIKit.framework/UIView.json"
    "UIKit.framework/UIViewController.json"
    )

for c in ${CPY[@]}; do
    base=`basename "${c}"`
    framework=`dirname "${c}"`
    dir="${framework%\.framework}"
    in_path="${1}/$c"
    out_path="${dir}/${base}"

    # Create output directory.
    if [[ ! -e "${dir}" ]]; then
        mkdir -p "${dir}"
    fi

    # Check if input file exists.
    if [[ ! -e "${in_path}" ]]; then
        echo -e "File doesn't exists ${in_path}"
        continue
    fi

    # Copy.
    echo -e "Copying: ${out_path}"
    cp "${in_path}" "${out_path}"
done

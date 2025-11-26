# -*- coding: utf-8 -*-
from burp import (
    IBurpExtender,
    IHttpListener,
    IContextMenuFactory,
    IExtensionStateListener,
)
from java.util import ArrayList
from javax.swing import JMenuItem
import random, string, uuid, re

try:
    import rstr
except ImportError:
    rstr = None


class BurpExtender(
    IBurpExtender, IHttpListener, IContextMenuFactory, IExtensionStateListener
):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Burp Faker")
        callbacks.registerHttpListener(self)
        callbacks.registerContextMenuFactory(self)
        callbacks.registerExtensionStateListener(self)
        self._callbacks.printOutput(
            "Author: Bhavin Vasara\nGithub: github.com/itzzmegrrr"
        )
        self._callbacks.printOutput("[Burp Faker] Extension loaded successfully.")
        if rstr is None:
            self._callbacks.printOutput("rstr not found - regex faker disabled.")
        else:
            self._callbacks.printOutput("rstr found - regex faker enabled.")

        # tag -> {faker_type: value}
        self.tagged_values = {}

    def extensionUnloaded(self):
        self.tagged_values.clear()
        self._callbacks.printOutput("[Burp Faker] Unloaded and resources cleared.")

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if not messageIsRequest:
            return

        req_bytes = messageInfo.getRequest()
        req_str = self._helpers.bytesToString(req_bytes)
        tool_name = self._callbacks.getToolName(toolFlag)

        new_req_str = self.replace_placeholders(req_str, tool_name)
        if new_req_str != req_str:
            messageInfo.setRequest(self._helpers.stringToBytes(new_req_str))

    def replace_placeholders(self, text, tool_name):
        pattern = r"\{\{burp_faker\.([a-zA-Z]+)\((.*?)\)\}\}"
        matches = re.findall(pattern, text)

        for faker_type, raw_args in matches:
            args_dict = self.parse_args(raw_args)
            tag = args_dict.pop("tag", None)

            # Determine length if applicable
            faker_types_with_length = [
                "alpha",
                "lower",
                "upper",
                "numeric",
                "alphanumeric",
                "custom",
            ]
            length = 8
            charset = None
            regex_pattern = None

            if faker_type in faker_types_with_length:
                if "length" in args_dict:
                    length = int(args_dict["length"])
                elif "0" in args_dict:
                    length = int(args_dict["0"])
                if faker_type == "custom" and "charset" in args_dict:
                    charset = args_dict["charset"]
                elif faker_type == "custom" and "1" in args_dict:
                    charset = args_dict["1"]
            elif faker_type == "regex":
                if "0" in args_dict:
                    regex_pattern = args_dict["0"]

            key = (faker_type, tag)
            sliceable = faker_type in faker_types_with_length

            if tag and sliceable:
                # For tagged values, generate max length if not exists
                existing_val = self.tagged_values.get(key)
                if not existing_val or len(existing_val) < length:
                    val = self.generate_faker(
                        faker_type, length, charset, regex_pattern
                    )
                    self.tagged_values[key] = val
                value = self.tagged_values[key][:length]
            else:
                value = self.generate_faker(faker_type, length, charset, regex_pattern)

            placeholder = "{{burp_faker." + faker_type + "(" + raw_args + ")}}"
            text = text.replace(placeholder, value)
            self._callbacks.printOutput(
                "[" + tool_name + "] Replaced " + placeholder + " -> " + value
            )

        return text

    def parse_args(self, raw_args):
        args = [a.strip() for a in raw_args.split(",") if a.strip()]
        args_dict = {}
        for idx, arg in enumerate(args):
            if "=" in arg:
                k, v = arg.split("=", 1)
                args_dict[k.strip()] = v.strip()
            else:
                args_dict[str(idx)] = arg
        return args_dict

    def generate_faker(self, faker_type, length=8, charset=None, regex_pattern=None):
        if faker_type == "uuid":
            return str(uuid.uuid4())
        if faker_type == "alphanumeric":
            return "".join(
                random.choice(string.ascii_letters + string.digits)
                for _ in range(length)
            )
        if faker_type == "alpha":
            return "".join(random.choice(string.ascii_letters) for _ in range(length))
        if faker_type == "lower":
            return "".join(random.choice(string.ascii_lowercase) for _ in range(length))
        if faker_type == "upper":
            return "".join(random.choice(string.ascii_uppercase) for _ in range(length))
        if faker_type == "numeric":
            return "".join(random.choice(string.digits) for _ in range(length))
        if faker_type == "custom" and charset:
            return "".join(random.choice(charset) for _ in range(length))
        if faker_type == "regex" and regex_pattern:
            if rstr:
                return rstr.xeger(regex_pattern)
            return "REGEX_NOT_SUPPORTED(" + regex_pattern + ")"
        return "INVALID_PLACEHOLDER"

    def createMenuItems(self, invocation):
        menu = ArrayList()

        def add(label, val, enabled=True):
            item = JMenuItem(
                label,
                actionPerformed=lambda x, v=val: self.insert_placeholder(invocation, v),
            )
            item.setEnabled(enabled)
            menu.add(item)

        add("Insert uuid", "{{burp_faker.uuid()}}")
        add("Insert alphanumeric(16)", "{{burp_faker.alphanumeric(16)}}")
        add("Insert alpha(10)", "{{burp_faker.alpha(10)}}")
        add("Insert lower(10)", "{{burp_faker.lower(10)}}")
        add("Insert upper(10)", "{{burp_faker.upper(10)}}")
        add("Insert numeric(10)", "{{burp_faker.numeric(10)}}")
        add("Insert custom(10, abc123!@#)", "{{burp_faker.custom(10, abc123!@#)}}")
        # Regex menu always present, disabled if rstr not found
        add(
            "Insert regex",
            "{{burp_faker.regex([a-z]{3}[0-9]{2})}}",
            enabled=(rstr is not None),
        )
        return menu

    def insert_placeholder(self, invocation, placeholder):
        bounds = invocation.getSelectionBounds()
        if not bounds:
            return
        start, end = bounds
        message = invocation.getSelectedMessages()[0]

        req = message.getRequest()
        req_str = self._helpers.bytesToString(req)

        new_req = req_str[:start] + placeholder + req_str[end:]
        message.setRequest(self._helpers.stringToBytes(new_req))

        self._callbacks.printOutput(
            "[ContextMenu] Inserted placeholder: " + placeholder
        )

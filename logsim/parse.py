"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
import pdb
import sys
import pytest


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.symbol = self.scanner.get_symbol()

        self.name_string = ""
        self.device_id = 0
        self.output_id = 0
        self.input_id = 0
        self.input_device_id = 0
        self.output_device_id = 0

        self.switch_input = 0
        self.clock_cycle = 0
        self.no_inputs = 0

        self.devices_symbol_list = []
        self.device_input_dict = {}
        self.device_output_dict = {}
        self.monitored_outputs = []

        self.input_added = False
        self.output_added = False

        self.error_count = 0
        self.syntax_error_count = 0
        self.in_stopping_symbol = False

        self.device_error = False
        self.connection_error = False
        self.monitor_error = False

        self.name_error = False
        self.gate_error = False
        self.input_error = False
        self.output_error = False
        self.section_skipped = False

        self.defining = False
        self.connecting = False
        self.monitoring = False

        self.devices_instance = 0
        self.connections_instance = 0
        self.monitoring_instance = 0

    def parse_network(self):
        """Parse the circuit definition file."""

        # check if there is any file content
        if self.symbol.type == self.scanner.EOF:
            print("Error: No file content found")
            return False

        # circuit = devices, connections, monitor
        # loop through the sections until the end of the file is reached
        while self.symbol.type != self.scanner.EOF:
            self.device_error = False
            self.connection_error = False
            self.monitor_error = False
            if self.symbol.type == self.scanner.KEYWORD \
                    and self.symbol.id == self.scanner.DEVICES_ID:
                self.defining = True
                self.device_error = False
                self.devices_list()
                self.device_dictionary()
                self.defining = False
                self.devices_instance += 1
                if self.devices_instance > 1:
                    break
            elif (self.symbol.type == self.scanner.KEYWORD
                  and self.symbol.id == self.scanner.CONNECTIONS_ID) \
                    and self.devices_instance == 1:
                self.connecting = True
                self.connection_error = False
                self.connections_list()
                self.connecting = False
                self.connections_instance += 1
                if self.connections_instance > 1:
                    break
            elif (self.symbol.type == self.scanner.KEYWORD
                  and self.symbol.id == self.scanner.MONITOR_ID) \
                    and (self.connections_instance == 1
                         and self.devices_instance == 1):
                self.monitoring = True
                self.monitor_error = False
                self.monitor()
                self.monitoring = False
                self.monitoring_instance += 1
                if self.monitoring_instance > 1:
                    break
            elif self.symbol.id == self.scanner.HASHTAG:
                self.comment()
            else:
                break

        # if the sections haven't all been parsed once
        # and none have been skipped, not all sections are present
        if (self.devices_instance != 1 or
                self.connections_instance != 1 or
                self.monitoring_instance != 1) and \
                self.section_skipped is False:
            print("Error: Not all sections present")
            self.error_count += 1

        # return to logsim True if no errors have been found
        # return False if errors exist
        if self.error_count == 0:
            return True
        else:
            print(self.error_count)
            return False

    def error(self, error_type, stopping_symbol):
        """return error message and continue
         until stopping symbol before resuming parsing"""
        self.error_count += 1

        # return relevant error message
        if error_type == "NO_COMMA":
            print("Error: Expected a comma")
            self.syntax_error_count += 1
        elif error_type == "NO_COLON":
            print("Error: Expected a colon")
            self.syntax_error_count += 1
        elif error_type == "NO_DEVICES":
            print("Error: Expected an opening devices statement")
            self.syntax_error_count += 1
        elif error_type == "NO_CONNECTIONS":
            print("Error: Expected an opening connections statement")
            self.syntax_error_count += 1
        elif error_type == "NO_SEMICOLON":
            print("Error: Expected a semicolon")
            self.syntax_error_count += 1
        elif error_type == "NO_MONITOR":
            print("Error: Expected an opening monitor statement")
            self.syntax_error_count += 1
        elif error_type == "NO_IS":
            print("Error: Incorrect devices definition")
            self.syntax_error_count += 1
        elif error_type == "NO_GATE_TYPE":
            print("Error: Gate defined does not exist")
            self.syntax_error_count += 1
        elif error_type == "NO_GATE":
            print("Error: Gate expected")
            self.syntax_error_count += 1
        elif error_type == "NO_SWITCH":
            print("Error: Switch definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_CLOCK":
            print("Error: Clock definition expected")
            self.syntax_error_count += 1
        elif error_type == "SWITCH_INPUT":
            print("Error: Initial switch input of 0 or 1 expected")
            self.syntax_error_count += 1
        elif error_type == "CLOCK":
            print("Error: Clock definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_INTEGER":
            print("Error: Integer expected")
            self.syntax_error_count += 1
        elif error_type == "NO_CYCLE":
            print("Error: Cycle definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_AND":
            print("Error: AND definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_INPUT_NO":
            print("Error: Input number between 1 and 16 expected")
            self.syntax_error_count += 1
        elif error_type == "NO_INPUT":
            print("Error: Input definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_NAND":
            print("Error: NAND definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_OR":
            print("Error: OR definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_NOR":
            print("Error: NOR definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_DTYPE":
            print("Error: DTYPE definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_XOR":
            print("Error: XOR definition expected")
            self.syntax_error_count += 1
        elif error_type == "NO_CONNECTION":
            print("Error: Incorrect connection definition")
            self.syntax_error_count += 1
        elif error_type == "NO_INPUT_TYPE":
            print("Error: Input type does not exist")
            self.syntax_error_count += 1
        elif error_type == "NO_OUTPUT_TYPE":
            print("Error:Output type does not exist")
            self.syntax_error_count += 1
        elif error_type == "NO_CHARACTER":
            print("Error: Alphabetic character expected")
            self.syntax_error_count += 1
        elif error_type == "NO_CHARACTER_DIGIT":
            print("Error: Alphanumeric character expected")
            self.syntax_error_count += 1
        elif error_type == "NO_HASHTAG":
            print("Error: Hashtag expected")
            self.syntax_error_count += 1
        elif error_type == "NO_MONITOR_DEF":
            print("Error: Incorrect monitor definition")
            self.syntax_error_count += 1
        elif error_type == "DEVICE_EXISTS":
            print("Error: Device name already used")
        elif error_type == "NO_DEVICE":
            print("Error: Device has not been defined")
        elif error_type == "INPUT_USED":
            print("Error: Input has already been connected")
        elif error_type == "OUTPUT_MONITORED":
            print("Error: Output is already being monitored")
        elif error_type == "MONITOR_FAILED":
            print("Error: Output not being monitored")
        elif error_type == "CONNECTION_NOT_MADE":
            print("Error: Connection not made")

        # print pointer showing location of the error
        error_message = self.scanner.error_location()
        print(error_message[0], "\n", error_message[1], "\n", error_message[2])

        stopping_symbols = []
        go_to_next = []

        # get the stopping symbols and
        # whether they are associated with an advance
        # to the next character once reached
        for stop in stopping_symbol:
            stopping_symbols.append(stop[0])
            go_to_next.append(stop[1])

        # continue until a stopping symbol is reached
        if self.symbol.id in stopping_symbols:
            self.in_stopping_symbol = True
        else:
            self.in_stopping_symbol = False

        while not self.in_stopping_symbol and \
                self.symbol.type != self.scanner.EOF:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id in stopping_symbols:
                symbol_index = stopping_symbols.index(self.symbol.id)
                if go_to_next[symbol_index]:
                    self.symbol = self.scanner.get_symbol()
                self.in_stopping_symbol = True

    def devices_list(self):
        """devices= "DEVICES", ":", device, ";" ,
        {device, ";"}, "END DEVICES";"""
        # check syntax of devices list
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.PUNCTUATION \
                and self.symbol.id == self.scanner.COLON:
            self.symbol = self.scanner.get_symbol()
            self.device()
            # check for inline comment
            if self.symbol.id == self.scanner.HASHTAG:
                self.comment()
            # continue parsing devices until end of devices list reached
            # or until error is discovered
            while self.symbol.id != self.scanner.SEMICOLON:
                if self.device_error is False:
                    # end of devices list reached without semicolon
                    if (self.symbol.id == self.scanner.CONNECTIONS_ID
                        or self.symbol.id == self.scanner.MONITOR_ID) \
                            or self.symbol.type == self.scanner.EOF:
                        self.error("NO_SEMICOLON", [(self.scanner.CONNECTIONS_ID, False),
                                                    (self.scanner.MONITOR_ID, False)])
                        break
                    else:
                        self.device()
                        # check for comment
                        if self.symbol.id == self.scanner.HASHTAG:
                            self.comment()
                else:
                    break
            # end of devices section reached
            if self.symbol.id == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
                # check for comment
                if self.symbol.id == self.scanner.HASHTAG:
                    self.comment()
        else:
            self.error("NO_COLON", [(self.scanner.CONNECTIONS_ID, False),
                                    (self.scanner.MONITOR_ID, False)])

    def connections_list(self):
        """connections= "CONNECTIONS", ":", connection, ";",
        {connection, ";"}, "END CONNECTIONS";"""
        # check syntax of connections list
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.PUNCTUATION \
                and self.symbol.id == self.scanner.COLON:
            self.symbol = self.scanner.get_symbol()
            self.connection()
            # check for comment
            if self.symbol.id == self.scanner.HASHTAG:
                self.comment()
            # continue parsing until end of connections list reached
            # or until error in list is discovered
            if self.connection_error is False:
                if self.symbol.id == self.scanner.SEMICOLON:
                    self.symbol = self.scanner.get_symbol()
                while self.symbol.id != self.scanner.SEMICOLON:
                    if self.connection_error is False:
                        # end of connections list reached without semicolon
                        if self.symbol.id == self.scanner.MONITOR_ID \
                                or self.symbol.type == self.scanner.EOF:
                            self.error("NO_SEMICOLON", [(self.scanner.MONITOR_ID, False)])
                            break
                        else:
                            self.connection()
                            # check for comment
                            if self.symbol.id == self.scanner.HASHTAG:
                                self.comment()
                    else:
                        break
                # end of connections list reached
                if self.symbol.id == self.scanner.SEMICOLON:
                    self.symbol = self.scanner.get_symbol()
        else:
            self.error("NO_COLON", [(self.scanner.MONITOR_ID, False)])

    def monitor(self):
        """monitor = "MONITOR", output, {("and"| ",") output}, ";"""""
        # check syntax of monitor section
        self.symbol = self.scanner.get_symbol()
        self.output()
        # make monitor only if no errors have been found
        if self.error_count == 0:
            error_type = self.monitors.make_monitor(self.output_device_id, self.output_id)
            if error_type != self.monitors.NO_ERROR:
                self.error("MONITOR_FAILED", [(self.scanner.EOF, False)])
                self.section_skipped = True
        if self.monitor_error is False:
            # no and or comma or semicolon after first monitor
            if self.symbol.type == self.scanner.NAME:
                self.error("NO_MONITOR_DEF", [(self.scanner.SEMICOLON, True),
                                              (self.scanner.EOF, False)])
            else:
                # parse list of monitors
                while self.symbol.id == self.scanner.AND or \
                        self.symbol.type == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    if self.monitor_error is False:
                        self.output()
                        # make monitor if no errors found
                        if self.error_count == 0:
                            error_type = self.monitors.make_monitor(self.output_device_id, self.output_id)
                            if error_type != self.monitors.NO_ERROR:
                                self.error("MONITOR_FAILED", [(self.scanner.EOF, False)])
                                self.section_skipped = True
                        # end of file reached
                        if self.symbol.type == self.scanner.EOF:
                            break
                    else:
                        break
                # end of monitor section reached
                if self.symbol.id == self.scanner.SEMICOLON:
                    self.symbol = self.scanner.get_symbol()
                    # check for comment
                    if self.symbol.id == self.scanner.HASHTAG:
                        self.comment()
                else:
                    # end of file reached without semicolon
                    # error if no semantic error found
                    if self.section_skipped is False:
                        self.error("NO_SEMICOLON", [(self.scanner.EOF, False)])

    def device(self):
        """device = name, "is", gate, ";";"""
        # get id of the device and check name syntax
        self.device_id = self.name()
        # check syntax of device definition
        if self.device_error is False:
            if self.symbol.type == self.scanner.KEYWORD \
                    and self.symbol.id == self.scanner.IS:
                self.symbol = self.scanner.get_symbol()
                # check syntax of gate definition
                self.gate()
                if self.device_error is False:
                    # check for comma or semicolon
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                    elif self.symbol.id != self.scanner.SEMICOLON \
                            and self.symbol.type != self.scanner.KEYWORD \
                            and self.symbol.type != self.scanner.EOF:
                        self.error("NO_COMMA", [(self.scanner.COMMA, False),
                                                (self.scanner.CONNECTIONS_ID, False),
                                                (self.scanner.MONITOR_ID, False)])
                        # if parser returns to comma
                        # still in devices list so continue parsing
                        if self.symbol.id == self.scanner.COMMA:
                            self.symbol = self.scanner.get_symbol()
                            self.device_error = False
                        # if parser returns to next sections
                        # skip rest of devices list
                        else:
                            self.section_skipped = True
                            self.device_error = True
                else:
                    # after skipping rest of line after an error
                    # reset errors to false to continue parsing
                    if self.name_error:
                        self.name_error = False
                        self.device_error = False
                    elif self.gate_error:
                        self.gate_error = False
                        self.device_error = False
                    elif self.section_skipped:
                        self.device_error = True
            else:
                self.error("NO_IS", [(self.scanner.CONNECTIONS_ID, False),
                                     (self.scanner.MONITOR_ID, False),
                                     (self.scanner.COMMA, False)])
                # if parser returns to comma
                # still in devices list so continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.device_error = False
                # if parser returns to next sections
                # skip rest of devices list
                else:
                    self.section_skipped = True
                    self.device_error = True
        else:
            # after skipping rest of line after an error
            # reset errors to false to continue parsing
            if self.name_error:
                self.name_error = False
                self.device_error = False
            elif self.gate_error:
                self.gate_error = False
                self.device_error = False
            elif self.section_skipped:
                self.device_error = True

    def name(self):
        """name = character, {character|digit};"""
        # check syntax of name of device
        if self.symbol.type == self.scanner.NAME:
            # get id of device
            name_id = self.get_id(self.symbol)
            self.symbol = self.scanner.get_symbol()
            return name_id
        else:
            # change variable values to return to parsing at
            # correct position depending on stopping symbol returned
            # and section currently in
            if self.defining:
                self.error("NO_CHARACTER", [(self.scanner.COMMA, False),
                                            (self.scanner.CONNECTIONS_ID, False),
                                            (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma
                # still in devices list so continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.name_error = True
                # if parser returns to next sections
                # skip rest of devices list
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.device_error = True
            elif self.connecting:
                self.error("NO_CHARACTER", [(self.scanner.COMMA, False),
                                            (self.scanner.CONNECTIONS_ID, False),
                                            (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma
                # still in connections list so continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.name_error = True
                # if parser returns to next sections
                # skip rest of connections list
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.connection_error = True
            elif self.monitoring:
                self.error("NO_CHARACTER", [(self.scanner.SEMICOLON, False),
                                            (self.scanner.MONITOR_ID, False)])
                # skip rest of monitor section
                self.monitor_error = True
            else:
                self.device_error = True
                self.connection_error = True
                self.monitor_error = True

    def connection(self):
        """connection = output, "to", input;"""
        # check syntax of connection definition
        self.output()
        if self.connection_error is False:
            self.symbol = self.scanner.get_symbol()
            self.input()
            if self.connection_error is False:
                # make connection between input and output port
                # if no syntax errors have been found yet
                if self.syntax_error_count == 0:
                    error_type = self.network.make_connection(self.input_device_id,
                                                              self.input_id,
                                                              self.output_device_id,
                                                              self.output_id)
                    if error_type != self.network.NO_ERROR:
                        self.error("CONNECTION_NOT_MADE", [(self.scanner.EOF, False)])
                        self.connection_error = True
                        self.section_skipped = True
                # check for comma at end of connection definition
                if self.symbol.type == self.scanner.PUNCTUATION \
                        and self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                elif (self.symbol.type != self.scanner.PUNCTUATION
                      and self.symbol.id != self.scanner.SEMICOLON) \
                        and self.symbol.type != self.scanner.KEYWORD \
                        and self.symbol.type != self.scanner.EOF:
                    self.error("NO_COMMA", [(self.scanner.COMMA, False),
                                            (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma
                    # still in connections list so continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.connection_error = False
                    # if parser returns to monitor section
                    # skip rest of connections list
                    else:
                        self.section_skipped = True
                        self.connection_error = True
            else:
                # after skipping rest of line after an error
                # reset errors to false to continue parsing
                if self.name_error:
                    self.name_error = False
                    self.connection_error = False
                elif self.gate_error:
                    self.gate_error = False
                    self.connection_error = False
                elif self.section_skipped:
                    self.connection_error = True
                elif self.input_error:
                    self.input_error = False
                    self.connection_error = False
        else:
            # after skipping rest of line after an error
            # reset errors to false to continue parsing
            if self.name_error:
                self.name_error = False
                self.connection_error = False
            elif self.gate_error:
                self.gate_error = False
                self.connection_error = False
            elif self.section_skipped:
                self.connection_error = True
            elif self.output_error:
                self.output_error = False
                self.connection_error = False

    def input(self):
        """input = name, ".", (boolean_input | dtype_input);"""
        # get id of input device and check name syntax
        self.input_device_id = self.name()
        # check syntax of input definition
        if self.connection_error is False:
            if self.symbol.type == self.scanner.PUNCTUATION \
                    and self.symbol.id == self.scanner.FULLSTOP:
                self.symbol = self.scanner.get_symbol()
                # symbol returned for boolean input is I1, I2
                # take first character to check for I
                characters = [c for c in self.scanner.string]
                if self.symbol.type == self.scanner.NAME \
                        and characters[0] == "I":
                    self.boolean_input()
                # symbol returned for d-type input is DATA, CLK,
                # SET or CLEAR
                elif self.symbol.type == self.scanner.KEYWORD \
                        and (self.symbol.id == self.scanner.DATA or
                             self.symbol.id == self.scanner.CLK or
                             self.symbol.id == self.scanner.SET or
                             self.symbol.id == self.scanner.CLEAR):
                    self.dtype_input()
                else:
                    self.error("NO_INPUT_TYPE", [(self.scanner.COMMA, False),
                                                 (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.input_error = True
                    # if parser returns to next sections
                    # skip rest of current section
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.connection_error = True
            else:
                self.error("NO_INPUT_TYPE", [(self.scanner.COMMA, False),
                                             (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.input_error = True
                # if parser returns to next sections
                # skip rest of current section
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.connection_error = True

    def output(self):
        """output = name, [".", (dtype_output | clock_output)];"""
        # get id of output device and check name syntax
        self.output_device_id = self.name()
        if self.connection_error is False and \
                self.monitor_error is False:
            # check syntax of output
            if self.symbol.type == self.scanner.PUNCTUATION \
                    and self.symbol.id == self.scanner.FULLSTOP:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.id == self.scanner.Q \
                        or self.symbol.id == \
                        self.scanner.QBAR:
                    self.dtype_output()
                else:
                    self.error("NO_OUTPUT_TYPE", [(self.scanner.COMMA, False),
                                                  (self.scanner.MONITOR_ID, False)])
                    if self.connecting:
                        # if parser returns to comma continue parsing
                        if self.symbol.id == self.scanner.COMMA:
                            self.symbol = self.scanner.get_symbol()
                            self.output_error = True
                        # if parser returns to monitor
                        # skip rest of connections section
                        elif self.symbol.id == self.scanner.MONITOR_ID:
                            self.section_skipped = True
                        self.connection_error = True
                    elif self.monitoring:
                        self.monitor_error = True

            elif self.symbol.id != self.scanner.TO and \
                    self.symbol.type != self.scanner.EOF and \
                    self.monitoring is False:
                if self.symbol.type == self.scanner.NAME:
                    self.error("NO_CONNECTION", [(self.scanner.COMMA, False),
                                                 (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.output_error = True
                    # if parser returns to monitor
                    # skip rest of connections section
                    elif self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.connection_error = True
                else:
                    self.error("NO_OUTPUT_TYPE", [(self.scanner.COMMA, False),
                                                  (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.output_error = True
                    # if parser returns to monitor
                    # skip rest of connections section
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.connection_error = True
            # check monitor definition syntax after output
            elif self.symbol.id != self.scanner.AND and \
                    self.symbol.id != self.scanner.COMMA and \
                    self.symbol.id != self.scanner.SEMICOLON and \
                    self.symbol.type != self.scanner.EOF and \
                    self.monitoring is True:
                self.error("NO_MONITOR_DEF", [(self.scanner.EOF, False)])
                self.monitor_error = True
            else:
                if self.connecting:
                    # non d-type output id set to None
                    self.output_id = None
                    if self.error_count == 0:
                        # output added to device if no errors
                        self.output_added = self.devices.add_output(self.output_device_id,
                                                                    self.output_id)
                        if self.output_added is False:
                            print("Output not added")
                elif self.monitoring:
                    # non d-type output id set to None
                    self.output_id = None
                    # check if device is already monitored
                    if (self.output_device_id, self.output_id) in self.monitored_outputs:
                        self.error("OUTPUT_MONITORED", [(self.scanner.EOF, False)])
                        self.section_skipped = True
                        self.monitor_error = True
                    else:
                        # add device to monitored outputs
                        self.monitored_outputs.append((self.output_device_id, self.output_id))

    def gate(self):
        """gate = switch | clock | and |
        nand | or | nor | dtype | xor;"""
        # call relevant gate definition
        if self.symbol.type == self.scanner.KEYWORD:
            if self.symbol.id == self.scanner.SWITCH_ID:
                self.switch()
            elif self.symbol.id == self.scanner.CLOCK_ID:
                self.clock()
            elif self.symbol.id == self.scanner.AND_ID:
                self.and_gate()
            elif self.symbol.id == self.scanner.NAND_ID:
                self.nand_gate()
            elif self.symbol.id == self.scanner.OR_ID:
                self.or_gate()
            elif self.symbol.id == self.scanner.NOR_ID:
                self.nor_gate()
            elif self.symbol.id == self.scanner.DTYPE_ID:
                self.dtype()
            elif self.symbol.id == self.scanner.XOR_ID:
                self.xor()
            elif self.symbol.id == self.scanner.NOT_ID:
                self.not_gate()
            else:
                # no gate type found
                self.error("NO_GATE_TYPE", [(self.scanner.COMMA, False),
                                            (self.scanner.CONNECTIONS_ID, False),
                                            (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.gate_error = True
                # if parser returns to next sections
                # skip rest of current section
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.device_error = True
        else:
            self.error("NO_GATE", [(self.scanner.COMMA, False),
                                   (self.scanner.CONNECTIONS_ID, False),
                                   (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def switch(self):
        """switch = "SWITCH with state", inital_switch;"""
        # check syntax of switch definition
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.SWITCH_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.KEYWORD \
                    and self.symbol.id == self.scanner.WITH:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.KEYWORD \
                        and self.symbol.id == self.scanner.STATE:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.INT16 \
                            and (self.symbol.id == self.scanner.ZERO
                                 or self.symbol.id == self.scanner.ONE):
                        # get the initial input of the switch
                        self.switch_input = int(self.names.get_name_string(self.symbol.id))
                        if self.device_error is False:
                            # create a switch if no errors found
                            self.devices.make_switch(self.device_id, self.switch_input)
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.error("SWITCH_INPUT", [(self.scanner.COMMA, False),
                                                    (self.scanner.CONNECTIONS_ID, False),
                                                    (self.scanner.MONITOR_ID, False)])
                        # if parser returns to comma continue parsing
                        if self.symbol.id == self.scanner.COMMA:
                            self.symbol = self.scanner.get_symbol()
                            self.gate_error = True
                        # if parser returns to next sections
                        # skip rest of current section
                        elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                                self.symbol.id == self.scanner.MONITOR_ID:
                            self.section_skipped = True
                        self.device_error = True
                else:
                    self.error("NO_SWITCH", [(self.scanner.COMMA, False),
                                             (self.scanner.CONNECTIONS_ID, False),
                                             (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.gate_error = True
                    # if parser returns to next sections
                    # skip rest of current section
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.device_error = True
            else:
                self.error("NO_SWITCH", [(self.scanner.COMMA, False),
                                         (self.scanner.CONNECTIONS_ID, False),
                                         (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.gate_error = True
                # if parser returns to next sections
                # skip rest of current section
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.device_error = True
        else:
            self.error("NO_SWITCH", [(self.scanner.COMMA, False),
                                     (self.scanner.CONNECTIONS_ID, False),
                                     (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def clock(self):
        """clock = "CLOCK with", digit, "cycle period";"""
        # check syntax of clock definition
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.CLOCK_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.KEYWORD \
                    and self.symbol.id == self.scanner.WITH:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.INTEGER \
                        or self.symbol.type == self.scanner.INT16:
                    # get cycle period of clock
                    self.clock_cycle = int(self.names.get_name_string(self.symbol.id))
                    self.symbol = self.scanner.get_symbol()
                    # scanner returns each digit of number again
                    # therefore skip these digits
                    while self.symbol.type == self.scanner.INT16:
                        self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.KEYWORD \
                            and self.symbol.id == self.scanner.CYCLE:
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.KEYWORD \
                                and self.symbol.id == self.scanner.PERIOD:
                            if self.device_error is False:
                                # create clock if no errors found
                                self.devices.make_clock(self.device_id, self.clock_cycle)
                            self.symbol = self.scanner.get_symbol()
                        else:
                            self.error("NO_CYCLE", [(self.scanner.COMMA, False),
                                                    (self.scanner.SEMICOLON, False),
                                                    (self.scanner.CONNECTIONS_ID, False),
                                                    (self.scanner.MONITOR_ID, False)])
                            # if parser returns to comma continue parsing
                            if self.symbol.id == self.scanner.COMMA:
                                self.symbol = self.scanner.get_symbol()
                                self.gate_error = True
                            # if parser returns to next sections
                            # skip rest of current section
                            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                                    self.symbol.id == self.scanner.MONITOR_ID:
                                self.section_skipped = True
                            self.device_error = True
                    else:
                        self.error("NO_CYCLE", [(self.scanner.COMMA, False),
                                                (self.scanner.SEMICOLON, False),
                                                (self.scanner.CONNECTIONS_ID, False),
                                                (self.scanner.MONITOR_ID, False)])
                        # if parser returns to comma continue parsing
                        if self.symbol.id == self.scanner.COMMA:
                            self.symbol = self.scanner.get_symbol()
                            self.gate_error = True
                        # if parser returns to next sections
                        # skip rest of current section
                        elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                                self.symbol.id == self.scanner.MONITOR_ID:
                            self.section_skipped = True
                        self.device_error = True
                else:
                    self.error("NO_INTEGER", [(self.scanner.COMMA, False),
                                              (self.scanner.SEMICOLON, False),
                                              (self.scanner.CONNECTIONS_ID, False),
                                              (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.gate_error = True
                    # if parser returns to next sections
                    # skip rest of current section
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.device_error = True
            else:
                self.error("NO_CLOCK", [(self.scanner.COMMA, False),
                                        (self.scanner.SEMICOLON, False),
                                        (self.scanner.CONNECTIONS_ID, False),
                                        (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.gate_error = True
                # if parser returns to next sections
                # skip rest of current section
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.device_error = True
        else:
            self.error("NO_CLOCK", [(self.scanner.COMMA, False),
                                    (self.scanner.SEMICOLON, False),
                                    (self.scanner.CONNECTIONS_ID, False),
                                    (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def and_gate(self):
        """and = "AND with", number_inputs, ("input"|"inputs");"""
        # check syntax of AND gate
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.AND_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.KEYWORD \
                    and self.symbol.id == self.scanner.WITH:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.INT16 \
                        and self.symbol.id != self.scanner.ZERO:
                    # get number of inputs of AND gate
                    self.no_inputs = int(self.names.get_name_string(self.symbol.id))
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.KEYWORD \
                            and (self.symbol.id == self.scanner.INPUT or
                                 self.symbol.id == self.scanner.INPUTS):
                        if self.device_error is False:
                            # create an AND gate if no errors found
                            self.devices.make_gate(self.device_id, self.devices.AND, self.no_inputs)
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.error("NO_INPUT", [(self.scanner.COMMA, False),
                                                (self.scanner.CONNECTIONS_ID, False),
                                                (self.scanner.MONITOR_ID, False)])
                        # if parser returns to comma continue parsing
                        if self.symbol.id == self.scanner.COMMA:
                            self.symbol = self.scanner.get_symbol()
                            self.gate_error = True
                        # if parser returns to next sections
                        # skip rest of current section
                        elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                                self.symbol.id == self.scanner.MONITOR_ID:
                            self.section_skipped = True
                        self.device_error = True
                else:
                    self.error("NO_INPUT_NO", [(self.scanner.COMMA, False),
                                               (self.scanner.CONNECTIONS_ID, False),
                                               (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.gate_error = True
                    # if parser returns to next sections
                    # skip rest of current section
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.device_error = True
            else:
                self.error("NO_AND", [(self.scanner.COMMA, False),
                                      (self.scanner.CONNECTIONS_ID, False),
                                      (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.gate_error = True
                # if parser returns to next sections
                # skip rest of current section
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.device_error = True
        else:
            self.error("NO_AND", [(self.scanner.COMMA, False),
                                  (self.scanner.CONNECTIONS_ID, False),
                                  (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def nand_gate(self):
        """nand = "NAND with", number_inputs, ("input"|"inputs");"""
        # check syntax of NAND gate
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.NAND_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.KEYWORD \
                    and self.symbol.id == self.scanner.WITH:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.INT16 \
                        and self.symbol.id != self.scanner.ZERO:
                    # get number of inputs of NAND gate
                    self.no_inputs = int(self.names.get_name_string(self.symbol.id))
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.KEYWORD \
                            and (self.symbol.id == self.scanner.INPUT or
                                 self.symbol.id == self.scanner.INPUTS):
                        if self.device_error is False:
                            # create a NAND gate if no errors found
                            self.devices.make_gate(self.device_id, self.devices.NAND, self.no_inputs)
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.error("NO_INPUT", [(self.scanner.COMMA, False),
                                                (self.scanner.CONNECTIONS_ID, False),
                                                (self.scanner.MONITOR_ID, False)])
                        # if parser returns to comma continue parsing
                        if self.symbol.id == self.scanner.COMMA:
                            self.symbol = self.scanner.get_symbol()
                            self.gate_error = True
                        # if parser returns to next sections
                        # skip rest of current section
                        elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                                self.symbol.id == self.scanner.MONITOR_ID:
                            self.section_skipped = True
                        self.device_error = True
                else:
                    self.error("NO_INPUT_NO", [(self.scanner.COMMA, False),
                                               (self.scanner.CONNECTIONS_ID, False),
                                               (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.gate_error = True
                    # if parser returns to next sections
                    # skip rest of current section
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.device_error = True
            else:
                self.error("NO_NAND", [(self.scanner.COMMA, False),
                                       (self.scanner.CONNECTIONS_ID, False),
                                       (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.gate_error = True
                # if parser returns to next sections
                # skip rest of current section
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.device_error = True
        else:
            self.error("NO_NAND", [(self.scanner.COMMA, False),
                                   (self.scanner.CONNECTIONS_ID, False),
                                   (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def or_gate(self):
        """or = "OR with", number_inputs, ("input"|"inputs");"""
        # check syntax of OR gate
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.OR_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.KEYWORD \
                    and self.symbol.id == self.scanner.WITH:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.INT16 \
                        and self.symbol.id != self.scanner.ZERO:
                    # get number of inputs of OR gate
                    self.no_inputs = int(self.names.get_name_string(self.symbol.id))
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.KEYWORD \
                            and (self.symbol.id == self.scanner.INPUT or
                                 self.symbol.id == self.scanner.INPUTS):
                        if self.device_error is False:
                            # create an OR gate if no errors found
                            self.devices.make_gate(self.device_id, self.devices.OR, self.no_inputs)
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.error("NO_INPUT", [(self.scanner.COMMA, False),
                                                (self.scanner.CONNECTIONS_ID, False),
                                                (self.scanner.MONITOR_ID, False)])
                        # if parser returns to comma continue parsing
                        if self.symbol.id == self.scanner.COMMA:
                            self.symbol = self.scanner.get_symbol()
                            self.gate_error = True
                        # if parser returns to next sections
                        # skip rest of current section
                        elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                                self.symbol.id == self.scanner.MONITOR_ID:
                            self.section_skipped = True
                        self.device_error = True
                else:
                    self.error("NO_INPUT_NO", [(self.scanner.COMMA, False),
                                               (self.scanner.CONNECTIONS_ID, False),
                                               (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.gate_error = True
                    # if parser returns to next sections
                    # skip rest of current section
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.device_error = True
            else:
                self.error("NO_OR", [(self.scanner.COMMA, False),
                                     (self.scanner.CONNECTIONS_ID, False),
                                     (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.gate_error = True
                # if parser returns to next sections
                # skip rest of current section
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.device_error = True
        else:
            self.error("NO_OR", [(self.scanner.COMMA, False),
                                 (self.scanner.CONNECTIONS_ID, False),
                                 (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def nor_gate(self):
        """nor = "NOR with", number_inputs, ("input"|"inputs");"""
        # check syntax of NOR gate
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.NOR_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.KEYWORD \
                    and self.symbol.id == self.scanner.WITH:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.INT16 \
                        and self.symbol.id != \
                        self.scanner.ZERO:
                    # get number of inputs of NOR gate
                    self.no_inputs = int(self.names.get_name_string(self.symbol.id))
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.KEYWORD \
                            and (self.symbol.id ==
                                 self.scanner.INPUT or
                                 self.symbol.id ==
                                 self.scanner.INPUTS):
                        if self.device_error is False:
                            # make a NOR gate if no errors found
                            self.devices.make_gate(self.device_id, self.devices.NOR, self.no_inputs)
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.error("NO_INPUT", [(self.scanner.COMMA, False),
                                                (self.scanner.CONNECTIONS_ID, False),
                                                (self.scanner.MONITOR_ID, False)])
                        # if parser returns to comma continue parsing
                        if self.symbol.id == self.scanner.COMMA:
                            self.symbol = self.scanner.get_symbol()
                            self.gate_error = True
                        # if parser returns to next sections
                        # skip rest of current section
                        elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                                self.symbol.id == self.scanner.MONITOR_ID:
                            self.section_skipped = True
                        self.device_error = True
                else:
                    self.error("NO_INPUT_NO", [(self.scanner.COMMA, False),
                                               (self.scanner.CONNECTIONS_ID, False),
                                               (self.scanner.MONITOR_ID, False)])
                    # if parser returns to comma continue parsing
                    if self.symbol.id == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.gate_error = True
                    # if parser returns to next sections
                    # skip rest of current section
                    elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                            self.symbol.id == self.scanner.MONITOR_ID:
                        self.section_skipped = True
                    self.device_error = True
            else:
                self.error("NO_NOR", [(self.scanner.COMMA, False),
                                      (self.scanner.CONNECTIONS_ID, False),
                                      (self.scanner.MONITOR_ID, False)])
                # if parser returns to comma continue parsing
                if self.symbol.id == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.gate_error = True
                # if parser returns to next sections
                # skip rest of current section
                elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                        self.symbol.id == self.scanner.MONITOR_ID:
                    self.section_skipped = True
                self.device_error = True

    def dtype(self):
        """dtype = "DTYPE";"""
        # check syntax of d-type device
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.DTYPE_ID:
            if self.device_error is False:
                # make a d-type device if no errors found
                self.devices.make_d_type(self.device_id)
            self.symbol = self.scanner.get_symbol()
        else:
            self.error("NO_DTYPE", [(self.scanner.COMMA, False),
                                    (self.scanner.CONNECTIONS_ID, False),
                                    (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def xor(self):
        """xor = "XOR";"""
        # check syntax of XOR gate
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.XOR_ID:
            if self.device_error is False:
                # make a XOR gate if no errors found
                self.devices.make_gate(self.device_id, self.devices.XOR, 2)
            self.symbol = self.scanner.get_symbol()
        else:
            self.error("NO_XOR", [(self.scanner.COMMA, False),
                                  (self.scanner.CONNECTIONS_ID, False),
                                  (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def not_gate(self):
        """not = "NOT";"""
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.NOT_ID:
            if self.device_error is False:
                # make a NOT gate if no errors found
                self.devices.make_gate(self.device_id, self.devices.NOT, 1)
            self.symbol = self.scanner.get_symbol()
        else:
            self.error("NO_NOT", [(self.scanner.COMMA, False),
                                  (self.scanner.CONNECTIONS_ID, False),
                                  (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.gate_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.device_error = True

    def boolean_input(self):
        """boolean_input = "I", number_inputs;"""
        # check syntax of boolean input
        characters = [c for c in self.scanner.string]
        # check that number of inputs is between 1 and 16
        if 1 <= int(characters[1]) <= 16:
            if self.error_count == 0:
                # get input port id and add input if no errors found
                self.input_id = self.get_input_id(self.input_device_id)
                self.input_added = self.devices.add_input(self.input_device_id,
                                                          self.input_id)
                if self.input_added is False:
                    print("Input not added")
            self.symbol = self.scanner.get_symbol()
        else:
            self.error("NO_INPUT_NO", [(self.scanner.COMMA, False),
                                       (self.scanner.MONITOR_ID, False)])
            # if parser returns to comma continue parsing
            if self.symbol.id == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.input_error = True
            # if parser returns to next sections
            # skip rest of current section
            elif self.symbol.id == self.scanner.CONNECTIONS_ID or \
                    self.symbol.id == self.scanner.MONITOR_ID:
                self.section_skipped = True
            self.connection_error = True

    def dtype_input(self):
        """dtype_input = ("DATA" | "CLK" | "SET" | "CLEAR");"""
        # check syntax of d-type input
        if self.error_count == 0:
            # get input port id and add input if no errors found
            self.input_id = self.get_input_id(self.input_device_id)
            self.input_added = self.devices.add_input(self.input_device_id,
                                                      self.input_id)
            if self.input_added is False:
                print("Output not added")
        self.symbol = self.scanner.get_symbol()

    def dtype_output(self):
        """dtype_output = ("Q" | "QBAR");"""
        # check syntax of d-type output
        if self.connecting:
            if self.error_count == 0:
                # get output port id and add output if no errors found
                self.output_id = self.get_output_id(self.output_device_id)
                self.output_added = self.devices.add_output(self.output_device_id,
                                                            self.output_id)
                if self.output_added is False:
                    print("Output not added")
        elif self.monitoring:
            # get output port id of output to be monitored
            self.output_id = self.get_output_id(self.output_device_id)
        self.symbol = self.scanner.get_symbol()

    def get_id(self, device_name):
        """assign ids to devices and retrieve ids of devices"""
        symbol_id = device_name.id
        if self.defining:
            # assign id to device if id does not yet exist
            if symbol_id not in self.devices_symbol_list:
                self.devices_symbol_list.append(symbol_id)
                return symbol_id
            else:
                # semantic error raised in devices list
                self.error("DEVICE_EXISTS", [(self.scanner.EOF, False)])
                self.section_skipped = True
                self.device_error = True
                return None
        elif self.connecting or self.monitoring:
            # get id of device for connection or monitoring
            if symbol_id in self.devices_symbol_list:
                return symbol_id
            else:
                # if no syntax errors have been found
                # no lines have been skipped
                # and so all devices should have been defined
                if self.syntax_error_count == 0:
                    self.error("NO_DEVICE", [(self.scanner.EOF, False)])
                    self.section_skipped = True
                    self.connection_error = True
                return None

    def device_dictionary(self):
        """create two empty dictionaries with device ids as keys"""
        for symbol_id in self.devices_symbol_list:
            self.device_input_dict[symbol_id] = []
            self.device_output_dict[symbol_id] = []

    def get_input_id(self, device_name_id):
        """assign ids to input ports and retrieve existing ids"""
        # retrieve existing input port ids for device
        input_numbers = self.device_input_dict[device_name_id]
        # add new input port id to device
        if self.symbol.id not in input_numbers:
            self.device_input_dict[device_name_id].append(self.symbol.id)
            return self.symbol.id
        else:
            # if input port id already exists
            # input has been used in connection
            self.error("INPUT_USED", [(self.scanner.EOF, False)])
            self.section_skipped = True
            self.connection_error = True

    def get_output_id(self, device_name_id):
        """assign ids to output ports and retrieve existing ids"""
        # retrieve existing output port ids for device
        output_numbers = self.device_output_dict[device_name_id]
        # add new output port id to device
        if self.symbol.id not in output_numbers:
            self.device_output_dict[device_name_id].append(self.symbol.id)
            return self.symbol.id
        else:
            if self.monitoring:
                # if output port id exists in dictionary
                # and in monitored outputs
                # it is already being monitored
                if (device_name_id, self.symbol.id) in self.monitored_outputs:
                    self.error("OUTPUT_MONITORED", [(self.scanner.EOF, False)])
                    self.section_skipped = True
                    self.monitor_error = True
                else:
                    # add output port id to monitored outputs
                    self.monitored_outputs.append((device_name_id, self.symbol.id))

    def comment(self):
        """check syntax of comment"""
        if self.symbol.type == self.scanner.PUNCTUATION \
                and self.symbol.id == self.scanner.HASHTAG:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NAME or \
                    self.symbol.type == self.scanner.KEYWORD:
                self.symbol = self.scanner.get_symbol()
                while self.symbol.type == self.scanner.NAME or \
                        self.symbol.type == self.scanner.KEYWORD:
                    self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.PUNCTUATION \
                        and self.symbol.id == self.scanner.HASHTAG:
                    self.symbol = self.scanner.get_symbol()
                    # comment is at end of file
                    if self.symbol.type == self.scanner.EOF:
                        # if not all sections have been parsed
                        # error is raised in parse_network
                        if self.devices_instance == 0 or \
                            self.connections_instance == 0 or \
                                self.monitoring_instance == 0:
                            self.device_error = True
                            self.connection_error = True
                            self.monitor_error = True
                            self.section_skipped = False
                else:
                    self.error("NO_HASHTAG", [(self.scanner.EOF, False)])
                    # skip parsing to end of file
                    self.device_error = True
                    self.connection_error = True
                    self.monitor_error = True
                    self.section_skipped = True
            else:
                self.error("NO_CHARACTER_DIGIT", [(self.scanner.HASHTAG, True)])
                # skip parsing to end of file
                self.device_error = True
                self.connection_error = True
                self.monitor_error = True
                self.section_skipped = True
        else:
            self.error("NO_HASHTAG", [(self.scanner.HASHTAG, True)])
            # skip parsing to end of file
            self.device_error = True
            self.connection_error = True
            self.monitor_error = True
            self.section_skipped = True

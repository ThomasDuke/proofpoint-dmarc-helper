import wx
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from extract_msg import Message
# from msg_parser import MsgParser

# variables globales
x_proofpoint_headers = {}


class RecapFrame(wx.Frame):
    def __init__(self, parent, title, header_info):
        super(RecapFrame, self).__init__(parent, title=title, size=(500, 400))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        header_text = wx.TextCtrl(panel, value=header_info, style=wx.TE_MULTILINE|wx.HSCROLL)
        header_text.SetEditable(False)

        vbox.Add(header_text, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(vbox)
        self.Show()


class AnalyzerApp(wx.Frame):
    def __init__(self, parent, title):
        super(AnalyzerApp, self).__init__(parent, title=title, size=(700, 500))

        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.subject_label = wx.StaticText(self.panel, label="Insert your email file:")
        self.subject_input = wx.TextCtrl(self.panel)
        
        self.file_picker_button = wx.Button(self.panel, label="Choose File")
        self.file_picker_button.Bind(wx.EVT_BUTTON, self.on_file_pick)

        self.analyze_button = wx.Button(self.panel, label="Analyze ProofPoint headers")
        self.analyze_button.Bind(wx.EVT_BUTTON, self.parse_headers)

        self.recap_button = wx.Button(self.panel, label="Logs Details")
        self.recap_button.Bind(wx.EVT_BUTTON, self.show_recap)


        self.result_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.HSCROLL)


        vbox.Add(self.subject_label, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.subject_input, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.file_picker_button, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.analyze_button, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.recap_button, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.result_text, 1, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(vbox)
        self.Centre()
        self.Show()

    def on_file_pick(self, event):
        wildcard = "EML files (*.eml)|*.eml|MSG files (*.msg)|*.msg|All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Choose a file", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            global file_path
            file_path = dialog.GetPath()
            if file_path.lower().endswith(('.eml', '.msg')):
                self.subject_input.SetValue(file_path)
            else:
                wx.MessageBox("Please select a file with .eml or .msg extension.", "File Format Error", wx.OK | wx.ICON_ERROR)
            self.subject_input.SetValue(file_path)
        dialog.Destroy()
        return file_path

    def parse_headers(self, event):
        
        if file_path:
            if file_path.lower().endswith(('.eml')):
                with open(file_path, 'r') as file:
                    msg = email.message_from_file(file)
                    for header in msg._headers:
                        if header[0].startswith("X-Proofpoint"):
                            x_proofpoint_headers[header[0]] = header[1]
                    
                    header_info = ""
                    for key, value in x_proofpoint_headers.items():
                        header_info += f"{key}: {value}\n"
                    self.result_text.SetValue(header_info)
                    self.header_info = header_info
            # elif file_path.lower().endswith('.msg'):
                # msg = Message(file_path)
                # msg_obj = msg._msgobj

                # for key, val in msg_obj.items():
                #     if key.startswith("X-ProofPoint"):
                #         x_proofpoint_headers[key] = val

                # header_info = ""
                # for key, value in x_proofpoint_headers.items():
                #     header_info += f"{key}: {value}\n"

                # self.result_text.SetValue(header_info)
                # self.header_info = header_info

            elif file_path:
                wx.MessageBox("Please select a valid .eml or .msg file.", "File Format Error", wx.OK | wx.ICON_ERROR)

    def show_recap(self, event):
        if 'X-Proofpoint-Spam-Details' in x_proofpoint_headers:
            spam_details = x_proofpoint_headers['X-Proofpoint-Spam-Details']
            spam_details = spam_details.replace(' ', '\n')
            spam_details = spam_details.replace('\n\n', '\n')
            RecapFrame(None, "Policy Logs", spam_details)
        else:
            wx.MessageBox("No header X-Proofpoint-Spam-Details found.", "No Headers", wx.OK | wx.ICON_INFORMATION)

app = wx.App()
AnalyzerApp(None, title="ProofPoint Headers Analyzer")
app.MainLoop()

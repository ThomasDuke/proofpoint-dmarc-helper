import wx
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

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

        self.result_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.HSCROLL)


        vbox.Add(self.subject_label, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.subject_input, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.file_picker_button, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.analyze_button, 0, wx.EXPAND | wx.ALL, 5)        
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
        if file_path and file_path.lower().endswith(('.eml', '.msg')):
            with open(file_path, 'r') as file:
                msg = email.message_from_file(file)
                x_proofpoint_headers = {}
                for header in msg._headers:
                    if header[0].startswith("X-Proofpoint"):
                        x_proofpoint_headers[header[0]] = header[1]
                
                header_info = ""
                for key, value in x_proofpoint_headers.items():
                    header_info += f"{key}: {value}\n"
                self.result_text.SetValue(header_info)
        elif file_path:
            wx.MessageBox("Please select a valid .eml or .msg file.", "File Format Error", wx.OK | wx.ICON_ERROR)





app = wx.App()
AnalyzerApp(None, title="ProofPoint Headers Analyzer")
app.MainLoop()

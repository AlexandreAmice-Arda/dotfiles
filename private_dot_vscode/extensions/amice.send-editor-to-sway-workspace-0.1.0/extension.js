'use strict';

const childProcess = require('node:child_process');
const path = require('node:path');
const util = require('node:util');
const vscode = require('vscode');

const execFile = util.promisify(childProcess.execFile);
const SWAYMSG = '/usr/bin/swaymsg';
const TARGET_WORKSPACES = [1, 2, 3, 4];
const FOCUS_TIMEOUT_MS = 3000;
const POLL_INTERVAL_MS = 50;

let output;

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function swaymsg(args) {
  const { stdout } = await execFile(SWAYMSG, args, {
    encoding: 'utf8',
    maxBuffer: 10 * 1024 * 1024,
  });
  return stdout;
}

function findFocusedCodeWindow(node, workspaceNumber = undefined) {
  const currentWorkspace = node.type === 'workspace' ? node.num : workspaceNumber;

  const xwaylandClass = node.window_properties?.class?.toLowerCase();
  if (node.focused && (node.app_id === 'code' || xwaylandClass === 'code')) {
    return {
      containerId: node.id,
      workspaceNumber: currentWorkspace,
    };
  }

  for (const child of [...(node.nodes || []), ...(node.floating_nodes || [])]) {
    const result = findFocusedCodeWindow(child, currentWorkspace);
    if (result) {
      return result;
    }
  }

  return undefined;
}

async function focusedCodeWindow() {
  const tree = JSON.parse(await swaymsg(['--type', 'get_tree', '--raw']));
  return findFocusedCodeWindow(tree);
}

async function waitForDestination(targetWorkspace, sourceGroup) {
  const deadline = Date.now() + FOCUS_TIMEOUT_MS;

  while (Date.now() < deadline) {
    const focusedWindow = await focusedCodeWindow();
    const activeGroup = vscode.window.tabGroups.activeTabGroup;

    if (
      focusedWindow?.workspaceNumber === targetWorkspace &&
      activeGroup !== sourceGroup
    ) {
      return activeGroup;
    }

    await delay(POLL_INTERVAL_MS);
  }

  return undefined;
}

function activeTextTab(document) {
  const group = vscode.window.tabGroups.activeTabGroup;
  const tab = group.activeTab;

  if (!(tab?.input instanceof vscode.TabInputText)) {
    return undefined;
  }

  if (tab.input.uri.toString() !== document.uri.toString()) {
    return undefined;
  }

  return { group, tab };
}

async function moveActiveEditor(targetWorkspace) {
  const sourceEditor = vscode.window.activeTextEditor;
  if (!sourceEditor) {
    void vscode.window.showWarningMessage('Focus a text editor before moving it.');
    return;
  }

  const source = activeTextTab(sourceEditor.document);
  if (!source) {
    void vscode.window.showWarningMessage(
      'This editor type cannot yet be moved between Sway workspaces.'
    );
    return;
  }

  let sourceWindow;
  try {
    sourceWindow = await focusedCodeWindow();
  } catch (error) {
    output.appendLine(`Could not query Sway: ${String(error)}`);
    void vscode.window.showErrorMessage(
      'Could not contact Sway. The editor was not changed.'
    );
    return;
  }

  if (!sourceWindow?.workspaceNumber) {
    void vscode.window.showErrorMessage(
      'The focused VS Code window could not be matched to a Sway workspace.'
    );
    return;
  }

  if (sourceWindow.workspaceNumber === targetWorkspace) {
    void vscode.window.showInformationMessage(
      `This editor is already on Sway workspace ${targetWorkspace}.`
    );
    return;
  }

  const document = sourceEditor.document;
  const selections = [...sourceEditor.selections];
  const visibleRange = sourceEditor.visibleRanges[0];
  const sourceWorkspace = sourceWindow.workspaceNumber;

  try {
    await swaymsg(['workspace', 'number', String(targetWorkspace)]);
    const destinationGroup = await waitForDestination(targetWorkspace, source.group);

    if (!destinationGroup) {
      throw new Error(
        `No different VS Code editor group became active on workspace ${targetWorkspace}`
      );
    }

    const destinationEditor = await vscode.window.showTextDocument(document, {
      viewColumn: vscode.ViewColumn.Active,
      preview: source.tab.isPreview,
      preserveFocus: false,
    });

    destinationEditor.selections = selections;
    if (visibleRange) {
      destinationEditor.revealRange(
        visibleRange,
        vscode.TextEditorRevealType.InCenterIfOutsideViewport
      );
    }

    await delay(POLL_INTERVAL_MS);
    const destinationWindow = await focusedCodeWindow();
    const destinationTab = vscode.window.tabGroups.activeTabGroup.activeTab;
    const openedUri =
      destinationTab?.input instanceof vscode.TabInputText
        ? destinationTab.input.uri.toString()
        : undefined;

    if (
      destinationWindow?.workspaceNumber !== targetWorkspace ||
      openedUri !== document.uri.toString()
    ) {
      throw new Error('VS Code did not verify the editor in the destination window');
    }

    const closed = await vscode.window.tabGroups.close(source.tab, true);
    if (!closed) {
      void vscode.window.showWarningMessage(
        `${path.basename(document.fileName)} opened on workspace ${targetWorkspace}, ` +
          `but its original tab remains on workspace ${sourceWorkspace}.`
      );
      return;
    }

    void vscode.window.setStatusBarMessage(
      `Moved ${path.basename(document.fileName)} to Sway workspace ${targetWorkspace}`,
      3000
    );
  } catch (error) {
    output.appendLine(
      `Move to workspace ${targetWorkspace} failed: ${error?.stack || String(error)}`
    );
    void vscode.window.showErrorMessage(
      `Could not move the editor to workspace ${targetWorkspace}. ` +
        'The original tab was left open.'
    );
  }
}

function activate(context) {
  output = vscode.window.createOutputChannel('Send Editor to Sway Workspace');
  context.subscriptions.push(output);

  for (const workspaceNumber of TARGET_WORKSPACES) {
    const command = `sendEditorToSway.workspace${workspaceNumber}`;
    context.subscriptions.push(
      vscode.commands.registerCommand(command, () =>
        moveActiveEditor(workspaceNumber)
      )
    );
  }
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};

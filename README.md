Welcome to the Healthcare Services Analytics & Decision Science Atlas.

This site is in its very early stages - please check back as we continue to develop it.

In time, we hope this can develop into a tool to help showcase the amazing work happening across the analyics and data science communities in healthcare, promoting reuse and collaborative work on the tools we all need.


## Contributing

Contributions are very welcome!

### Contributing a tool, package or project

#### via GitHub Issues (code-free approach!)

If you wish to submit a tool, package or project but are not confident with GitHub and Quarto (or you just have a simple submission to make), you can submit a GitHub issue via our template: [https://github.com/hsma-programme/decision_intelligence_atlas/issues/new/choose](https://github.com/hsma-programme/decision_intelligence_atlas/issues/new/choose)

This will collect all the required information and use it to automatically generate a new folder and file in the correct format, raising it as a 'pull request' for inclusion in the atlas. A repository administrator will then review the auto-created file, make any tweaks and fixes required, and let you know when your contribution is live.

#### Advanced option: contributing a .qmd file

If you wish to have more control over your submission and are comfortable using Quarto, you may wish to **take a fork of the repository**, make your changes, and then submit a pull request. Your request will be reviewed and merged, with additions or tweaks possible.

You can find a template .qmd file for adding a package, project or tool in the **templates** folder.

Templates for other kinds of content will follow in the future.

When creating your own entry,

- please create a folder in the **packages_projects_tools** folder with the name of the tool. Please ensure there are no spaces or special characters other than - or _ in the folder name.
- please then copy the template into your folder and rename it with the same name as your folder, ensuring you don't accidentally remove the .qmd file extension.
- you can then use this folder to store any additional resources such as images or gifs. Please use **relative** links - e.g. if you add an image called 'my_tool_example.png' to your folder 'my_tool', in your 'my_tool.qmd' file you would reference that as ![](my_tool_example.png), not ![](C:/my_username/decision_intelligence_atlas/packages_projects_tools/my_tool/my_tool_example.png) or !(my_tool/my_tool_example.png).
- please fill in the yml header, using the comments provided to help guide you
- please provide a description of the project outside of the yml header.
- categories that are currently in use can be found in templates/packages_projects_tools_permitted_categories.csv
- if you feel that an appropriate category doesn't currently exist for your addition, please add it in to the categories section of the yml header and mention it in your pull request. An administrator will then decide whether the new category will be added to the list of categories.
    - in addition, if you feel that it doesn't fit under any of the headers on the [atlas.hsma.co.uk/packages_tools_projects](atlas.hsma.co.uk/packages_tools_projects) page, please let us know in your pull request and an admin can look at adding a new section to this page. Please let us know if you have a section heading in mind.

The website is currently being compiled with Quarto version 1.7.33. You do not need to render the project yourself other than to preview your entry - all site rendering is handled by automated GitHub actions.

##### Using GitHub Codespaces

If you wish to avoid having to clone the repository to your local machine and set up Quarto, you may like to try editing in GitHub codespaces. All GitHub accounts have a fairly generous free number of minutes available for codespace usage per month.

Take a fork as normal using the fork button on the repository.

![](assets/2025-11-12-13-49-31.png)

Then click on 'code' --> 'open in codespaces'.

![](assets/2025-11-12-13-48-34.png)

It will take a few minutes, but you should then be presented with a web-based version of VSCode with the repository cloned and the appropriat version of Quarto pre-installed. You can then use the built-in GitHub features of the web-based VSCode to commit your changes to your fork and make a pull request when you are ready.

### Contributing a technique or graph example

Templates for these types of contributions have not yet been set up - please check back soon!

Alternatively, if you're up for the challenge of creating a template, please do feel free to raise an issue to discuss or create a pull request with your proposal.

### Making other suggestions

If you have any other suggestions about the website layout, content, or anything else, please [raise an issue]() on the repository.

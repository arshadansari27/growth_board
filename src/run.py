from integration.jira_api import update_notion_projects
from integration.rescuetime_to_notion import update_apps
from integration.toggle_to_notion import update_hotspots

if __name__ == '__main__':
    #context = in_memory_context_factory()
    #service = BoardService(context)
    #e = service.new("name", "description")
    #print(e.id, e.name, e.description)
    #test_board_status_up_down()

    update_notion_projects()
    update_hotspots()
    update_apps()
    '''
    from notion.block import TodoBlock
    client = get_client()
    url = 'https://www.notion.so/Data-Platform-ddeea775e1a24922ac2c33ff27b6d5b0#066a70468a5b47d5b2df1edaf7879b3c'
    block = client.get_block(url)
    print(block)
    print(block.title)
    '''

                if event.key == pygame.K_SPACE:
                    # try to select the card
                    selected = grid.get_item(cursor_x,cursor_y)
                    if not selected.flipped:
                        game_state['scale'] += selected.value
                        selected.flip()

                        # now check for combos
                        row_coords, col_coords = grid.get_related_coords(cursor_x,cursor_y)
                        row_cards,_  = grid.get_tiles_from_coords(row_coords)
                        col_cards,_ = grid.get_tiles_from_coords(col_coords)

                        new_cards = []
                        valid_coords = []

                        if sum([int(b.flipped) for b in col_cards]) == GRID_SIZE: #OK!
                            valid_coords.append(row_coords)

                        if sum([int(b.flipped) for b in row_cards]) == GRID_SIZE: #OK!
                            valid_coords.append(col_coords)
                        
                        for i in valid_coords:
                            new_cards.append(Card(random.randint(1,3), i[0], i[1]))
                        
                        grid.set_tiles_from_coords(valid_coords,new_cards) 
                    #print(grid.grid[cursor_y][cursor_x])
                    pass